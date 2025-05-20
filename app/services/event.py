"""
Event service module.

This module contains the business logic for event management, including CRUD operations,
recurrence handling, conflict detection, and versioning.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import json
import copy

from app.schemas.user import User, UserRole
from app.schemas.event import Event, EventPermission, EventVersion, RecurrencePattern
from app.models.event import EventCreate, EventUpdate, EventResponse
from app.utils.rbac import RoleChecker


class EventService:
    """Service for event-related operations."""
    
    @staticmethod
    def create_event(
        db: Session, 
        event_in: EventCreate, 
        current_user: User
    ) -> Event:
        """
        Create a new event.
        
        Args:
            db: Database session
            event_in: Event data
            current_user: Current user (event owner)
            
        Returns:
            Event: Created event
        """
        # Create the event
        event = Event(
            title=event_in.title,
            description=event_in.description,
            start_time=event_in.start_time,
            end_time=event_in.end_time,
            location=event_in.location,
            is_recurring=event_in.is_recurring,
            recurrence_pattern=event_in.recurrence_pattern,
            recurrence_rule=event_in.recurrence_rule,
            owner_id=current_user.id
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        # Create initial version
        EventService.create_event_version(
            db=db,
            event=event,
            user_id=current_user.id,
            change_description="Initial creation"
        )
        
        return event
    
    @staticmethod
    def update_event(
        db: Session, 
        event: Event, 
        event_in: EventUpdate, 
        current_user: User
    ) -> Event:
        """
        Update an event.
        
        Args:
            db: Database session
            event: Event to update
            event_in: Updated event data
            current_user: Current user (performing the update)
            
        Returns:
            Event: Updated event
        """
        # Keep track of changes for version history
        changes = []
        
        # Handle each field that might be updated
        if event_in.title is not None and event_in.title != event.title:
            changes.append(f"Title changed from '{event.title}' to '{event_in.title}'")
            event.title = event_in.title
            
        if event_in.description is not None and event_in.description != event.description:
            changes.append("Description updated")
            event.description = event_in.description
            
        if event_in.start_time is not None and event_in.start_time != event.start_time:
            changes.append(f"Start time changed from '{event.start_time}' to '{event_in.start_time}'")
            event.start_time = event_in.start_time
            
        if event_in.end_time is not None and event_in.end_time != event.end_time:
            changes.append(f"End time changed from '{event.end_time}' to '{event_in.end_time}'")
            event.end_time = event_in.end_time
            
        if event_in.location is not None and event_in.location != event.location:
            changes.append(f"Location changed from '{event.location}' to '{event_in.location}'")
            event.location = event_in.location
            
        if event_in.is_recurring is not None and event_in.is_recurring != event.is_recurring:
            changes.append(f"Recurring status changed from '{event.is_recurring}' to '{event_in.is_recurring}'")
            event.is_recurring = event_in.is_recurring
            
        if event_in.recurrence_pattern is not None and event_in.recurrence_pattern != event.recurrence_pattern:
            changes.append(f"Recurrence pattern changed from '{event.recurrence_pattern}' to '{event_in.recurrence_pattern}'")
            event.recurrence_pattern = event_in.recurrence_pattern
            
        if event_in.recurrence_rule is not None and event_in.recurrence_rule != event.recurrence_rule:
            changes.append("Recurrence rule updated")
            event.recurrence_rule = event_in.recurrence_rule
        
        # Increment version and update timestamp
        event.version += 1
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        # Create new version
        change_description = "; ".join(changes) if changes else "Event updated (no changes detected)"
        EventService.create_event_version(
            db=db,
            event=event,
            user_id=current_user.id,
            change_description=change_description
        )
        
        return event
    
    @staticmethod
    def delete_event(db: Session, event: Event) -> None:
        """
        Delete an event.
        
        Args:
            db: Database session
            event: Event to delete
        """
        db.delete(event)
        db.commit()
    
    @staticmethod
    def get_events(
        db: Session, 
        current_user: User,
        skip: int = 0, 
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """
        Get list of events accessible to the current user, with optional date filtering.
        
        Args:
            db: Database session
            current_user: Current user
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return (pagination)
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List[Event]: List of accessible events
        """
        # Base query for events owned by the user
        query = db.query(Event).filter(
            or_(
                # User is the owner
                Event.owner_id == current_user.id,
                # User has permission
                Event.id.in_(
                    db.query(EventPermission.event_id)
                    .filter(EventPermission.user_id == current_user.id)
                    .subquery()
                )
            )
        )
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(Event.end_time >= start_date)
        if end_date:
            query = query.filter(Event.start_time <= end_date)
        
        # Apply pagination and return results
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
        """
        Get event by ID.
        
        Args:
            db: Database session
            event_id: Event ID
            
        Returns:
            Optional[Event]: Event if found, None otherwise
        """
        return db.query(Event).filter(Event.id == event_id).first()
    
    @staticmethod
    def create_event_version(
        db: Session, 
        event: Event, 
        user_id: int,
        change_description: str = None
    ) -> EventVersion:
        """
        Create a new version of an event.
        
        Args:
            db: Database session
            event: Event to version
            user_id: User ID who made the change
            change_description: Optional description of changes
            
        Returns:
            EventVersion: New event version
        """
        # Create JSON snapshot of the event
        event_data = {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat() if event.start_time else None,
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "location": event.location,
            "is_recurring": event.is_recurring,
            "recurrence_pattern": event.recurrence_pattern.value if event.recurrence_pattern else None,
            "recurrence_rule": event.recurrence_rule,
            "owner_id": event.owner_id,
            "version": event.version,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "updated_at": event.updated_at.isoformat() if event.updated_at else None
        }
        
        # Create version record
        event_version = EventVersion(
            event_id=event.id,
            version=event.version,
            data=event_data,
            changed_by_id=user_id,
            change_description=change_description
        )
        
        db.add(event_version)
        db.commit()
        db.refresh(event_version)
        
        return event_version
    
    @staticmethod
    def get_event_versions(db: Session, event_id: int) -> List[EventVersion]:
        """
        Get all versions of an event.
        
        Args:
            db: Database session
            event_id: Event ID
            
        Returns:
            List[EventVersion]: List of event versions
        """
        return db.query(EventVersion).filter(
            EventVersion.event_id == event_id
        ).order_by(EventVersion.version.desc()).all()
    
    @staticmethod
    def get_event_version(
        db: Session, 
        event_id: int, 
        version: int
    ) -> Optional[EventVersion]:
        """
        Get a specific version of an event.
        
        Args:
            db: Database session
            event_id: Event ID
            version: Version number
            
        Returns:
            Optional[EventVersion]: Event version if found, None otherwise
        """
        return db.query(EventVersion).filter(
            EventVersion.event_id == event_id,
            EventVersion.version == version
        ).first()
    
    @staticmethod
    def rollback_event(
        db: Session, 
        event: Event, 
        version: int, 
        current_user: User
    ) -> Event:
        """
        Rollback an event to a previous version.
        
        Args:
            db: Database session
            event: Event to rollback
            version: Version to rollback to
            current_user: Current user
            
        Returns:
            Event: Updated event
        """
        # Get the specified version
        event_version = EventService.get_event_version(db, event.id, version)
        if not event_version:
            return None
        
        # Get the version data
        version_data = event_version.data
        
        # Update the event fields to match the version
        event.title = version_data.get("title", event.title)
        event.description = version_data.get("description", event.description)
        
        # Handle date fields
        if "start_time" in version_data and version_data["start_time"]:
            event.start_time = datetime.fromisoformat(version_data["start_time"])
        if "end_time" in version_data and version_data["end_time"]:
            event.end_time = datetime.fromisoformat(version_data["end_time"])
            
        event.location = version_data.get("location", event.location)
        event.is_recurring = version_data.get("is_recurring", event.is_recurring)
        
        # Handle enum fields
        if "recurrence_pattern" in version_data and version_data["recurrence_pattern"]:
            event.recurrence_pattern = RecurrencePattern(version_data["recurrence_pattern"])
        
        event.recurrence_rule = version_data.get("recurrence_rule", event.recurrence_rule)
        
        # Increment version
        event.version += 1
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        # Create new version record
        EventService.create_event_version(
            db=db,
            event=event,
            user_id=current_user.id,
            change_description=f"Rolled back to version {version}"
        )
        
        return event
    
    @staticmethod
    def detect_conflicts(
        db: Session, 
        event_in: EventCreate, 
        user_id: int,
        event_id: Optional[int] = None
    ) -> List[Event]:
        """
        Detect conflicting events for a user.
        
        Args:
            db: Database session
            event_in: Event data to check for conflicts
            user_id: User ID to check conflicts for
            event_id: Optional event ID to exclude from conflict check (for updates)
            
        Returns:
            List[Event]: List of conflicting events
        """
        # Base query for events owned by or shared with the user
        query = db.query(Event).filter(
            or_(
                # User is the owner
                Event.owner_id == user_id,
                # User has permission
                Event.id.in_(
                    db.query(EventPermission.event_id)
                    .filter(EventPermission.user_id == user_id)
                    .subquery()
                )
            )
        )
        
        # Exclude the current event if event_id is provided (for updates)
        if event_id:
            query = query.filter(Event.id != event_id)
        
        # Check for time conflicts
        conflicts = query.filter(
            and_(
                # New event starts before existing event ends
                event_in.start_time < Event.end_time,
                # New event ends after existing event starts
                event_in.end_time > Event.start_time
            )
        ).all()
        
        return conflicts
    
    @staticmethod
    def calculate_diff(
        db: Session,
        event_id: int,
        version1: int,
        version2: int
    ) -> Dict[str, Any]:
        """
        Calculate differences between two event versions.
        
        Args:
            db: Database session
            event_id: Event ID
            version1: First version for comparison
            version2: Second version for comparison
            
        Returns:
            Dict[str, Any]: Dictionary of differences
        """
        # Get both versions
        event_version1 = EventService.get_event_version(db, event_id, version1)
        event_version2 = EventService.get_event_version(db, event_id, version2)
        
        if not event_version1 or not event_version2:
            return None
        
        # Get the data from both versions
        data1 = event_version1.data
        data2 = event_version2.data
        
        # Calculate differences
        diff = {}
        
        # Compare each field
        for key in set(list(data1.keys()) + list(data2.keys())):
            # Skip metadata fields
            if key in ["id", "created_at", "updated_at"]:
                continue
                
            # Check if field exists in both versions
            value1 = data1.get(key)
            value2 = data2.get(key)
            
            # Add to diff if values are different
            if value1 != value2:
                diff[key] = {
                    "version1": value1,
                    "version2": value2
                }
        
        return diff
    
    @staticmethod
    def share_event(
        db: Session,
        event: Event,
        user_id: int,
        role: UserRole
    ) -> EventPermission:
        """
        Share an event with another user.
        
        Args:
            db: Database session
            event: Event to share
            user_id: User ID to share with
            role: Role to assign
            
        Returns:
            EventPermission: Created permission
        """
        # Check if permission already exists
        existing_permission = db.query(EventPermission).filter(
            EventPermission.event_id == event.id,
            EventPermission.user_id == user_id
        ).first()
        
        if existing_permission:
            # Update existing permission
            existing_permission.role = role
            db.add(existing_permission)
            db.commit()
            db.refresh(existing_permission)
            return existing_permission
        
        # Create new permission
        permission = EventPermission(
            event_id=event.id,
            user_id=user_id,
            role=role
        )
        
        db.add(permission)
        db.commit()
        db.refresh(permission)
        
        return permission
    
    @staticmethod
    def get_event_permissions(
        db: Session,
        event_id: int
    ) -> List[EventPermission]:
        """
        Get all permissions for an event.
        
        Args:
            db: Database session
            event_id: Event ID
            
        Returns:
            List[EventPermission]: List of permissions
        """
        return db.query(EventPermission).filter(
            EventPermission.event_id == event_id
        ).all()
    
    @staticmethod
    def update_permission(
        db: Session,
        event_id: int,
        user_id: int,
        role: UserRole
    ) -> Optional[EventPermission]:
        """
        Update a user's permission for an event.
        
        Args:
            db: Database session
            event_id: Event ID
            user_id: User ID
            role: New role
            
        Returns:
            Optional[EventPermission]: Updated permission if found, None otherwise
        """
        permission = db.query(EventPermission).filter(
            EventPermission.event_id == event_id,
            EventPermission.user_id == user_id
        ).first()
        
        if not permission:
            return None
        
        permission.role = role
        db.add(permission)
        db.commit()
        db.refresh(permission)
        
        return permission
    
    @staticmethod
    def remove_permission(
        db: Session,
        event_id: int,
        user_id: int
    ) -> bool:
        """
        Remove a user's permission for an event.
        
        Args:
            db: Database session
            event_id: Event ID
            user_id: User ID
            
        Returns:
            bool: True if permission was removed, False otherwise
        """
        permission = db.query(EventPermission).filter(
            EventPermission.event_id == event_id,
            EventPermission.user_id == user_id
        ).first()
        
        if not permission:
            return False
        
        db.delete(permission)
        db.commit()
        
        return True
    
    @staticmethod
    def batch_create_events(
        db: Session,
        events_in: List[EventCreate],
        current_user: User
    ) -> List[Event]:
        """
        Create multiple events in a batch.
        
        Args:
            db: Database session
            events_in: List of event data
            current_user: Current user
            
        Returns:
            List[Event]: List of created events
        """
        events = []
        
        for event_in in events_in:
            # Create the event
            event = Event(
                title=event_in.title,
                description=event_in.description,
                start_time=event_in.start_time,
                end_time=event_in.end_time,
                location=event_in.location,
                is_recurring=event_in.is_recurring,
                recurrence_pattern=event_in.recurrence_pattern,
                recurrence_rule=event_in.recurrence_rule,
                owner_id=current_user.id
            )
            
            db.add(event)
            events.append(event)
        
        # Commit all events at once
        db.commit()
        
        # Refresh all events to get their IDs
        for event in events:
            db.refresh(event)
            
            # Create initial version for each event
            EventService.create_event_version(
                db=db,
                event=event,
                user_id=current_user.id,
                change_description="Initial creation (batch)"
            )
        
        return events
