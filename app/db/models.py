"""
Database models initialization module.

This module imports all models to ensure proper initialization and registration with SQLAlchemy.
It resolves circular dependencies by importing everything here.
"""

# Import the Base class and database session
from app.schemas.base import Base
from app.db.base import SessionLocal, engine

# Import all models to register them
from app.schemas.user import User, UserRole
from app.schemas.event import (
    Event, 
    EventPermission, 
    EventVersion,
    RecurrencePattern
)

# Function to create all tables in the database
def create_all():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
