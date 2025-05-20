# Collaborative Event Management System

A FastAPI-based backend system for managing collaborative events with version control and real-time updates.

## Features

- 🔐 JWT Authentication and RBAC
- 📅 Event Management with Recurrence
- 👥 Collaboration Features
- 📝 Version Control & Change History
- 🔄 Real-time Updates
- 📚 OpenAPI Documentation

## Project Structure

```
app/
├── api/          # API routes and endpoints
├── core/         # Core application configuration
├── db/           # Database models and configuration
├── models/       # Pydantic models for request/response
├── schemas/      # SQLAlchemy ORM models
├── services/     # Business logic layer
└── utils/        # Utility functions and helpers
```

## Setup & Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Initialize the database:
   ```bash
   alembic upgrade head
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Role-Based Access Control

Three roles are supported:
- Owner: Full access to event
- Editor: Can modify event details
- Viewer: Can only view event details

## Development

This project follows:
- SOLID principles
- Clean Architecture patterns
- Comprehensive documentation
- Type hints and validation
- Proper error handling
