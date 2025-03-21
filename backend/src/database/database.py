from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from dotenv import load_dotenv
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate required environment variables
required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Get database connection details from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine with optimized connection pool settings
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Increased for better concurrency
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections every 30 minutes
    pool_pre_ping=True,  # Enable connection health checks
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "keepalives": 1,      # Enable TCP keepalive
        "keepalives_idle": 60  # Idle time before sending keepalive
    }
)

# Verify database connection
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("Database connection successful")
except SQLAlchemyError as e:
    logger.error(f"Failed to connect to database: {str(e)}")
    raise

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session with enhanced error handling and retry logic
def get_db():
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test the connection with proper error handling
            try:
                db.execute(text("SELECT 1"))
                yield db
            except SQLAlchemyError as e:
                logger.error(f"Database query failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database query error"
                )
            finally:
                db.close()
            return
        except SQLAlchemyError as e:
            if attempt == max_retries - 1:
                logger.error(f"Database connection failed after {max_retries} attempts: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database connection error"
                )
            logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            time.sleep(retry_delay * (attempt + 1))  # Exponential backoff