from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3
import os

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./medicines.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# For reflection with existing database
metadata = MetaData()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_exists():
    """Check if medicines.db exists"""
    return os.path.exists("medicines.db")

def get_medicine_table():
    """Get the existing medicine table using reflection"""
    metadata.reflect(bind=engine)
    if 'medicines' in metadata.tables:
        return metadata.tables['medicines']
    return None

def execute_raw_query(query: str):
    """Execute raw SQL query"""
    with engine.connect() as connection:
        result = connection.execute(query)
        return result.fetchall()