"""
Pydantic models for event-related requests and responses.

This module defines the data validation and serialization models for the API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator

from app.schemas.event import RecurrencePattern
from app.schemas.user import UserRole

# ==================== Request Models ====================

class EventPermissionCreate(BaseModel):
    """Model for creating event permissions."""
    user_id: int
    role: UserRole

class EventPermissionUpdate(BaseModel):
    """Model for updating event permissions."""
    role: UserRole

class EventBase(BaseModel):
    """Base model for event data."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = RecurrencePattern.NONE
    recurrence_rule: Optional[Dict[str, Any]] = None
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        """Validate that end_time is after start_time."""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v
    
    @validator('recurrence_rule')
    def validate_recurrence_rule(cls, v, values):
        """
        Validate that recurrence_rule is provided if recurrence_pattern is CUSTOM.
        And not provided if recurrence_pattern is not CUSTOM.
        """
        recurrence_pattern = values.get('recurrence_pattern')
        if recurrence_pattern == RecurrencePattern.CUSTOM and not v:
            raise ValueError('recurrence_rule must be provided when recurrence_pattern is CUSTOM')
        if recurrence_pattern != RecurrencePattern.CUSTOM and v:
            raise ValueError('recurrence_rule should only be provided when recurrence_pattern is CUSTOM')
        return v

class EventCreate(EventBase):
    """Model for event creation requests."""
    pass

class EventUpdate(BaseModel):
    """Model for event update requests."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_rule: Optional[Dict[str, Any]] = None
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        """Validate that end_time is after start_time if both are provided."""
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class EventBatchCreate(BaseModel):
    """Model for batch event creation requests."""
    events: List[EventCreate]

# ==================== Response Models ====================

class EventPermissionResponse(BaseModel):
    """Model for event permission responses."""
    id: int
    user_id: int
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        """Configure ORM compatibility."""
        orm_mode = True

class EventVersionResponse(BaseModel):
    """Model for event version responses."""
    id: int
    version: int
    changed_by_id: int
    created_at: datetime
    change_description: Optional[str] = None
    
    class Config:
        """Configure ORM compatibility."""
        orm_mode = True

class EventResponse(EventBase):
    """Model for event responses."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    version: int
    
    class Config:
        """Configure ORM compatibility."""
        orm_mode = True

class EventDetailResponse(EventResponse):
    """Model for detailed event responses including permissions."""
    permissions: List[EventPermissionResponse] = []
    
    class Config:
        """Configure ORM compatibility."""
        orm_mode = True

class EventVersionDetailResponse(BaseModel):
    """Model for detailed event version responses."""
    id: int
    version: int
    data: Dict[str, Any]  # Full event data at that version
    changed_by_id: int
    created_at: datetime
    change_description: Optional[str] = None
    
    class Config:
        """Configure ORM compatibility."""
        orm_mode = True

class EventChangelogResponse(BaseModel):
    """Model for event changelog responses."""
    versions: List[EventVersionResponse]
    
    class Config:
        """Configure ORM compatibility."""
        orm_mode = True

class EventDiffResponse(BaseModel):
    """Model for diff between two event versions."""
    version1: int
    version2: int
    diff: Dict[str, Any]  # Field-by-field differences
    
    class Config:
        """Configure ORM compatibility."""
        orm_mode = True
