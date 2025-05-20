"""
Main application module.

This module initializes the FastAPI application and includes all routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.endpoints import auth, events

# Import models module to ensure all models are registered
from app.db import models

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["authentication"]
)

app.include_router(
    events.router,
    prefix=f"{settings.API_V1_PREFIX}/events",
    tags=["events"]
)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Create all database tables on application startup
@app.on_event("startup")
def startup_event():
    """Initialize application on startup."""
    models.create_all()
