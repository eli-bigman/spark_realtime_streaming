import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Note: In the Docker container, these might already be set, but load_dotenv helps mainly for local dev/testing
load_dotenv()

class Settings:
    # Database Settings
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "ecommerce_db")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    
    # App Settings
    INPUT_DATA_DIR = os.getenv("INPUT_DATA_DIR", "./data/input")
    EVENTS_PER_SECOND = float(os.getenv("EVENTS_PER_SECOND", 1.0))
    BATCH_PROCESSING_TIME = int(os.getenv("BATCH_PROCESSING_TIME", 5))  # seconds
    
    @classmethod
    def get_jdbc_url(cls):
        return f"jdbc:postgresql://{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}?stringtype=unspecified"
    
    @classmethod
    def get_db_properties(cls):
        return {
            "user": cls.POSTGRES_USER,
            "password": cls.POSTGRES_PASSWORD,
            "driver": "org.postgresql.Driver"
        }

settings = Settings()
