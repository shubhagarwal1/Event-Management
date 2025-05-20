"""
Setup database tables script.

This script directly creates the tables needed for the application
using SQLAlchemy, bypassing Alembic migration issues.
"""

import sys
from sqlalchemy import inspect, text
from app.db.base import engine
from app.schemas.base import Base
from app.schemas.user import User, UserRole
from app.schemas.event import Event, EventPermission, EventVersion, RecurrencePattern

def setup_database():
    """Create database tables if they don't exist."""
    # Get inspector to check existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"Existing tables: {existing_tables}")
    
    # Check if we need to create tables
    tables_to_create = []
    if 'events' not in existing_tables:
        tables_to_create.append('events')
        print("Will create events table")
    
    if 'event_permissions' not in existing_tables:
        tables_to_create.append('event_permissions')
        print("Will create event_permissions table")
    
    if 'event_versions' not in existing_tables:
        tables_to_create.append('event_versions')
        print("Will create event_versions table")
    
    if not tables_to_create:
        print("All tables already exist. No action needed.")
        return
    
    # Create enum types if needed
    with engine.connect() as conn:
        # Check if enum types exist
        result = conn.execute(text("""
            SELECT typname FROM pg_type 
            JOIN pg_catalog.pg_namespace ON pg_namespace.oid = pg_type.typnamespace
            WHERE typname = 'userrole' OR typname = 'recurrencepattern';
        """))
        
        existing_enums = [row[0] for row in result]
        print(f"Existing enum types: {existing_enums}")
        
        # Create UserRole enum if needed
        if 'userrole' not in existing_enums:
            print("Creating userrole enum type")
            conn.execute(text("""
                CREATE TYPE userrole AS ENUM ('owner', 'editor', 'viewer');
            """))
        
        # Create RecurrencePattern enum if needed
        if 'recurrencepattern' not in existing_enums:
            print("Creating recurrencepattern enum type")
            conn.execute(text("""
                CREATE TYPE recurrencepattern AS ENUM (
                    'none', 'daily', 'weekly', 'monthly', 'yearly', 'custom'
                );
            """))
        
        conn.commit()
    
    # Create tables
    print("Creating tables...")
    Base.metadata.create_all(engine, 
                             tables=[Base.metadata.tables[table] for table in tables_to_create])
    
    print("Database setup completed successfully!")

if __name__ == "__main__":
    setup_database()
