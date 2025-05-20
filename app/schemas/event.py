"""
Event-related SQLAlchemy models.

This module defines the database models for event management, permissions, and versioning.
"""

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, JSON, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from app.schemas.base import Base
from app.schemas.user import UserRole

class EventPermission(Base):
    """Model for event permissions linking users to events with specific roles."""
    
    __tablename__ = "event_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="permissions")
    user = relationship("User", back_populates="event_permissions")
    
    class Config:
        """SQLAlchemy ORM config."""
        orm_mode = True

class RecurrencePattern(enum.Enum):
    """Enumeration of possible recurrence patterns for events."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"  # For more complex patterns defined in recurrence_rule

class Event(Base):
    """Model for events with versioning and permissions support."""
    
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    location = Column(String, nullable=True)
    
    # Recurrence fields
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(Enum(RecurrencePattern), default=RecurrencePattern.NONE)
    recurrence_rule = Column(JSON, nullable=True)  # Advanced recurrence rules (RFC 5545)
    
    # Ownership and tracking
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    version = Column(Integer, default=1, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="events")
    permissions = relationship("EventPermission", back_populates="event", cascade="all, delete-orphan")
    versions = relationship("EventVersion", back_populates="event", cascade="all, delete-orphan")
    
    class Config:
        """SQLAlchemy ORM config."""
        orm_mode = True

class EventVersion(Base):
    """Model for storing event version history."""
    
    __tablename__ = "event_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)  # Version number
    data = Column(JSON, nullable=False)  # Full event data snapshot
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    change_description = Column(Text, nullable=True)  # Optional description of changes
    
    # Relationships
    event = relationship("Event", back_populates="versions")
    changed_by = relationship("User")
    
    class Config:
        """SQLAlchemy ORM config."""
        orm_mode = True
        
    __table_args__ = (
        # Ensure each version number is unique per event
        UniqueConstraint('event_id', 'version', name='uix_event_version'),
    )
