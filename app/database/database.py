from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate DATABASE_URL is set
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is not set.")
    print("Please set DATABASE_URL with your database connection string.")
    # Don't exit here, let the application handle it during startup
    # sys.exit(1)  # Commented out to prevent early exit

# Determine if using PostgreSQL vs SQLite for engine configuration
if "postgresql" in DATABASE_URL.lower():
    # PostgreSQL-specific engine configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,           # Verify connections before use
        pool_recycle=300,             # Recycle connections every 5 minutes
        pool_size=20,                 # Number of connection pools
        max_overflow=30,              # Additional connections beyond pool_size
        echo=False                    # Set to True only for debugging
    )
elif "sqlite" in DATABASE_URL.lower():
    # SQLite-specific engine configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False                    # Set to True only for debugging
    )
else:
    print(f"Error: Unsupported database type in DATABASE_URL: {DATABASE_URL}")
    sys.exit(1)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to test database connectivity
def test_db_connection():
    """
    Test basic database connectivity by executing a simple query.
    This can be called at startup to verify the database connection.
    """
    try:
        db = SessionLocal()
        # Execute a simple query to test connection
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        return result is not None
    except Exception as e:
        print(f"Database connectivity test failed: {str(e)}")
        return False