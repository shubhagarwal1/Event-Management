"""
Authentication API endpoints.

This module implements the authentication-related API endpoints including
registration, login, refresh token, and logout functionality.
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.auth import AuthenticationService
from app.models.user import UserCreate, User as UserResponse
from app.schemas.user import User
from app.db.base import get_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    Decode JWT token to get current user.
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        User: Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Check token expiration
        expire = payload.get("exp")
        if expire is None:
            raise credentials_exception
        if datetime.utcnow() > datetime.fromtimestamp(expire):
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> User:
    """
    Register a new user.
    
    Args:
        db: Database session
        user_in: User creation data
        
    Returns:
        User: Created user data
        
    Raises:
        HTTPException: If user with same email already exists
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=AuthenticationService.get_password_hash(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login.
    
    Args:
        db: Database session
        form_data: OAuth2 form data
        
    Returns:
        dict: Access token and token type
        
    Raises:
        HTTPException: If authentication fails
    """
    user = AuthenticationService.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthenticationService.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Refresh access token.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: New access token and token type
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthenticationService.create_access_token(
        data={"sub": current_user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout() -> Any:
    """
    Logout endpoint.
    
    Note: With JWT, actual logout happens on the client side by removing the token.
    This endpoint is provided for compatibility and future extensions.
    
    Returns:
        dict: Success message
    """
    return {"message": "Successfully logged out"}
