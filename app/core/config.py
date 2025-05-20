"""
Core configuration module for the application.

This module handles loading and validating configuration from environment variables
using Pydantic's BaseSettings model.
"""

from typing import Any, Dict, Optional, List, Union
from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    """Application settings with environment variable validation."""
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    PROJECT_NAME: str = "Event Management System"
    VERSION: str = "1.0.0"
    
    # Database Configuration
    DATABASE_URL: PostgresDsn
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Validate and process CORS origins configuration."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        """Pydantic configuration class."""
        case_sensitive = True
        env_file = ".env"


# Create global settings instance
settings = Settings()
