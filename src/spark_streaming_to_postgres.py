from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
import sys
import os

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
        StructField("metadata", StringType(), True)    # Ingest as JSON string
    ])

def write_to_postgres(batch_df, batch_id):
    """
    Function to write each micro-batch to PostgreSQL.
    """
    print(f"Processing Batch ID: {batch_id} with {batch_df.count()} records")
    
    jdbc_url = settings.get_jdbc_url()
    # When running inside docker, "localhost" in settings might need to be resolved to "postgres"
    # However, settings.py reads env vars, and docker-compose sets POSTGRES_HOST=postgres
    
    db_properties = settings.get_db_properties()
    
    print(f"Writing batch {batch_id} to Postgres...")
    batch_df.write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "ecommerce_events") \
        .option("user", db_properties["user"]) \
        .option("password", db_properties["password"]) \
        .option("driver", db_properties["driver"]) \
        .mode("append") \
        .save()
    print(f"Successfully wrote batch {batch_id} to Postgres.")

def main():
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    print("Spark Session created successfully.")
    
    # 1. Read Stream
    print(f"Monitoring directory: {settings.INPUT_DATA_DIR}")
    
    # Ensure input directory exists
    os.makedirs(settings.INPUT_DATA_DIR, exist_ok=True)
    
    raw_df = spark.readStream \
        .format("json") \
        .schema(get_schema()) \
        .option("maxFilesPerTrigger", 10) \
        .load(settings.INPUT_DATA_DIR)
    
    # 2. Transform
    # Convert timestamp string to TimestampType
    processed_df = raw_df \
        .withColumn("timestamp", to_timestamp(col("timestamp"))) \
        .filter(col("event_id").isNotNull())
    
    # 3. Write Stream
    query = processed_df.writeStream \
        .foreachBatch(write_to_postgres) \
        .outputMode("append") \
        .option("checkpointLocation", "data/output/checkpoint") \
        .start()
    
    query.awaitTermination()

if __name__ == "__main__":
    main()
