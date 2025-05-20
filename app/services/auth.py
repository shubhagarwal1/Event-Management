"""
Authentication service module.

This module handles user authentication, password hashing, and JWT token management.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
# Import SQLAlchemy User model
from app.schemas.user import User
# Import Pydantic models for responses
from app.models.user import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthenticationService:
    """Service class for handling authentication-related operations."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional token expiration time
            
        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            db: Database session
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Optional[User]: Authenticated user or None
        """
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not AuthenticationService.verify_password(password, user.hashed_password):
            return None
        return user
