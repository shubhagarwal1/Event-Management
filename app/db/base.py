"""
Database configuration module.

This module sets up the SQLAlchemy engine and session management.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.schemas.base import Base

# Create SQLAlchemy engine
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,  # Enable connection pool "pre-ping" feature
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency to be used in FastAPI dependency injection.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
