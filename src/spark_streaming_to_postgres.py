from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
import sys
import os
import psycopg2
from psycopg2.extras import execute_values

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import settings

def get_spark_session():
    """
    Initialize Spark Session with Postgres JDBC driver.
    """
    return SparkSession.builder \
        .appName("EcommerceRealTimeIngestion") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.2") \
        .getOrCreate()

def get_schema():
    """
    Define the schema for the incoming JSON events.
    """
    return StructType([
        StructField("event_id", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("timestamp", StringType(), True),  # Ingest as string, convert later
        StructField("metadata", StringType(), True),   # Ingest as JSON string
        # New fields
        StructField("price", StringType(), True),      # Will convert to decimal
        StructField("quantity", StringType(), True),   # Will convert to integer
        StructField("discount_applied", StringType(), True),  # Will convert to boolean
        StructField("product_category", StringType(), True),
        StructField("session_id", StringType(), True)
    ])

def get_metadata_schema():
    """
    Define the schema for parsing the metadata JSON field.
    This enables extraction of device, browser, and location fields.
    """
    return StructType([
        StructField("device", StringType(), True),
        StructField("browser", StringType(), True),
        StructField("location", StringType(), True)
    ])

def write_to_postgres_upsert(batch_df, batch_id):
    """
    Custom upsert function using psycopg2 with comprehensive error handling.
    Handles duplicate event_ids by updating existing records using ON CONFLICT.
    
    Error handling ensures the stream continues even if a batch fails.
    """
    print(f"Processing Batch ID: {batch_id} with {batch_df.count()} records")
    
    if batch_df.isEmpty():
        print(f"Batch {batch_id} is empty. Skipping.")
        return
    
    try:
        # Collect data from Spark DataFrame
        rows = batch_df.collect()
        
        # Prepare data for insertion
        values = []
        for row in rows:
            values.append((
                row.event_id,
                row.event_type,
                row.user_id,
                row.product_id,
                row.timestamp,
                row.metadata,
                row.device,
                row.browser,
                row.location,
                row.ingestion_timestamp,
                row.price,
                row.quantity,
                row.discount_applied,
                row.product_category,
                row.session_id
            ))
        
        # Connect to PostgreSQL with error handling
        try:
            conn = psycopg2.connect(
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                dbname=settings.POSTGRES_DB,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT
            )
            
            cur = conn.cursor()
            
            # Upsert SQL with ON CONFLICT
            upsert_sql = """
                INSERT INTO ecommerce_events (
                    event_id, event_type, user_id, product_id, timestamp, 
                    metadata, device, browser, location, ingestion_timestamp,
                    price, quantity, discount_applied, product_category, session_id
                )
                VALUES %s
                ON CONFLICT (event_id)
                DO UPDATE SET
                    event_type = EXCLUDED.event_type,
                    user_id = EXCLUDED.user_id,
                    product_id = EXCLUDED.product_id,
                    timestamp = EXCLUDED.timestamp,
                    metadata = EXCLUDED.metadata,
                    device = EXCLUDED.device,
                    browser = EXCLUDED.browser,
                    location = EXCLUDED.location,
                    ingestion_timestamp = EXCLUDED.ingestion_timestamp,
                    price = EXCLUDED.price,
                    quantity = EXCLUDED.quantity,
                    discount_applied = EXCLUDED.discount_applied,
                    product_category = EXCLUDED.product_category,
                    session_id = EXCLUDED.session_id;
            """
            
            # Execute batch upsert
            execute_values(cur, upsert_sql, values)
            conn.commit()
            
            print(f"Successfully upserted {len(values)} records for batch {batch_id}")
            
            cur.close()
            conn.close()
            
        except psycopg2.Error as db_error:
            print(f"DATABASE ERROR in batch {batch_id}: {str(db_error)}")
            import traceback
            traceback.print_exc()
            # Close connection if it exists
            try:
                if 'conn' in locals() and conn:
                    conn.close()
            except:
                pass
                
    except Exception as e:
        print(f"CRITICAL ERROR in batch {batch_id}: {str(e)}")
        # Log the error but don't crash the stream
        import traceback
        traceback.print_exc()

def main():
    """
    Main function to run the Spark streaming job with comprehensive error handling.
    """
    spark = None
    query = None
    
    try:
        # 1. Initialize Spark Session
        print("Initializing Spark Session...")
        try:
            spark = get_spark_session()
            spark.sparkContext.setLogLevel("WARN")
            print("Spark Session created successfully.")
        except Exception as spark_error:
            print(f"FATAL ERROR: Failed to create Spark session: {str(spark_error)}")
            import traceback
            traceback.print_exc()
            print("Cannot proceed without Spark session. Exiting.")
            return
        
        # 2. Setup Input Directory
        print(f"Monitoring directory: {settings.INPUT_DATA_DIR}")
        try:
            os.makedirs(settings.INPUT_DATA_DIR, exist_ok=True)
            print(f"Input directory ready: {settings.INPUT_DATA_DIR}")
        except Exception as dir_error:
            print(f"WARNING: Failed to create input directory: {str(dir_error)}")
            print("Proceeding anyway - directory might already exist.")
        
        # 3. Read Stream
        print("Setting up stream reader...")
        try:
            raw_df = spark.readStream \
                .format("json") \
                .schema(get_schema()) \
                .option("maxFilesPerTrigger", 10) \
                .load(settings.INPUT_DATA_DIR)
            print("Stream reader configured successfully.")
        except Exception as read_error:
            print(f"FATAL ERROR: Failed to setup stream reader: {str(read_error)}")
            import traceback
            traceback.print_exc()
            if spark:
                spark.stop()
            return
        
        # 4. Apply Transformations
        print("Applying transformations...")
        try:
            # Parse metadata JSON and extract fields
            processed_df = raw_df \
                .withColumn("timestamp", to_timestamp(col("timestamp"))) \
                .withColumn("metadata_struct", from_json(col("metadata"), get_metadata_schema())) \
                .withColumn("device", col("metadata_struct.device")) \
                .withColumn("browser", col("metadata_struct.browser")) \
                .withColumn("location", col("metadata_struct.location")) \
                .withColumn("ingestion_timestamp", current_timestamp()) \
                .withColumn("price", col("price").cast("decimal(10,2)")) \
                .withColumn("quantity", col("quantity").cast("integer")) \
                .withColumn("discount_applied", col("discount_applied").cast("boolean")) \
                .drop("metadata_struct")  # Drop the temporary struct column
            print("Transformations applied successfully.")
        except Exception as transform_error:
            print(f"FATAL ERROR: Failed to apply transformations: {str(transform_error)}")
            import traceback
            traceback.print_exc()
            if spark:
                spark.stop()
            return
        
        # 5. Apply Data Validation Filters
        print("Applying data validation filters...")
        try:
            valid_df = processed_df \
                .filter(col("event_id").isNotNull()) \
                .filter(col("timestamp").isNotNull()) \
                .filter(col("event_type").isin(["view", "click", "purchase", "add_to_cart"]))
            print("Valid event types: view, click, purchase, add_to_cart")
            print("Validation filters applied successfully.")
        except Exception as filter_error:
            print(f"FATAL ERROR: Failed to apply validation filters: {str(filter_error)}")
            import traceback
            traceback.print_exc()
            if spark:
                spark.stop()
            return
        
        # 6. Start Streaming Write
        print(f"Starting streaming write with {settings.BATCH_PROCESSING_TIME}-second trigger interval...")
        try:
            query = valid_df.writeStream \
                .foreachBatch(write_to_postgres_upsert) \
                .trigger(processingTime=f'{settings.BATCH_PROCESSING_TIME} seconds') \
                .outputMode("update") \
                .option("checkpointLocation", "data/output/checkpoint") \
                .start()
            
            print("=" * 60)
            print("Streaming job started successfully!")
            print(f"Processing batches every {settings.BATCH_PROCESSING_TIME} seconds...")
            print("Upsert logic enabled: Duplicate event_ids will be updated, not rejected.")
            print("=" * 60)
        except Exception as stream_error:
            print(f"FATAL ERROR: Failed to start streaming write: {str(stream_error)}")
            import traceback
            traceback.print_exc()
            if spark:
                spark.stop()
            return
        
        # 7. Wait for Stream Termination
        try:
            print("Waiting for streaming query to terminate...")
            print("Press Ctrl+C to stop.")
            query.awaitTermination()
        except KeyboardInterrupt:
            print("\nReceived interrupt signal. Stopping streaming job gracefully...")
            if query:
                query.stop()
            print("Streaming job stopped.")
        except Exception as termination_error:
            print(f"ERROR during stream execution: {str(termination_error)}")
            import traceback
            traceback.print_exc()
            if query:
                query.stop()
    
    except Exception as main_error:
        print(f"UNEXPECTED ERROR in main function: {str(main_error)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\nCleaning up resources...")
        if query:
            try:
                query.stop()
                print("Streaming query stopped.")
            except:
                pass
        if spark:
            try:
                spark.stop()
                print("Spark session stopped.")
            except:
                pass
        print("Cleanup complete. Exiting.")

if __name__ == "__main__":
    main()
