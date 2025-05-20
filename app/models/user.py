"""
Pydantic models for user-related requests and responses.

This module defines the data validation and serialization models for the API.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, constr

class UserBase(BaseModel):
    """Base user model with common attributes."""
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    """Model for user creation requests."""
    password: constr(min_length=8)

class UserUpdate(UserBase):
    """Model for user update requests."""
    password: Optional[constr(min_length=8)]

class UserInDBBase(UserBase):
    """Base model for users in database."""
    id: int

    class Config:
        orm_mode = True

class User(UserInDBBase):
    """Model for user responses."""
    pass

class UserInDB(UserInDBBase):
    """Model for internal user representation."""
    hashed_password: str
