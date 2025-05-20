"""
User-related SQLAlchemy models.

This module defines the database models for user management and authentication.
"""

from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.schemas.base import Base
import enum

class UserRole(str, enum.Enum):
    """Enumeration of possible user roles."""
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"

class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships - defined with strings to avoid circular imports
    events = relationship("Event", back_populates="owner")
    event_permissions = relationship("EventPermission", back_populates="user")
