"""
Event API endpoints.

This module implements event-related API endpoints including CRUD operations,
collaboration features, and version history.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.user import User
from app.schemas.event import Event
from app.models.event import (
    EventCreate, EventUpdate, EventResponse, EventDetailResponse,
    EventPermissionCreate, EventPermissionResponse, EventPermissionUpdate,
    EventBatchCreate, EventVersionResponse, EventVersionDetailResponse,
    EventChangelogResponse, EventDiffResponse
)
from app.services.event import EventService
from app.utils.rbac import RoleChecker, get_event_with_permission_check
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

# ================== Event CRUD Operations ==================

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    *,
    db: Session = Depends(get_db),
    event_in: EventCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new event.
    
    Args:
        db: Database session
        event_in: Event creation data
        current_user: Current authenticated user
        
    Returns:
        EventResponse: Created event
        
    Raises:
        HTTPException: If there are conflicting events
    """
    # Check for conflicts
    conflicts = EventService.detect_conflicts(db, event_in, current_user.id)
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Event conflicts with {len(conflicts)} existing events"
        )
    
    # Create the event
    event = EventService.create_event(db, event_in, current_user)
    return event

@router.get("", response_model=List[EventResponse])
def read_events(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Any:
    """
    Get all events accessible to the current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        skip: Number of items to skip
        limit: Maximum number of items to return
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        List[EventResponse]: List of events
    """
    events = EventService.get_events(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )
    return events

@router.get("/{event_id}", response_model=EventDetailResponse)
def read_event(
    *,
    event: Event = Depends(get_event_with_permission_check),
) -> Any:
    """
    Get a specific event by ID.
    
    Args:
        event: Event (from dependency with permission check)
        
    Returns:
        EventDetailResponse: Event details
    """
    return event

@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    *,
    db: Session = Depends(get_db),
    event: Event = Depends(lambda event_id, db=Depends(get_db), current_user=Depends(get_current_user): 
                            get_event_with_permission_check(event_id, current_user, "edit", db)),
    event_in: EventUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update an event.
    
    Args:
        db: Database session
        event: Event to update (from dependency with permission check)
        event_in: Updated event data
        current_user: Current authenticated user
        
    Returns:
        EventResponse: Updated event
        
    Raises:
        HTTPException: If there are conflicting events
    """
    # If start or end time changed, check for conflicts
    if (event_in.start_time is not None and event_in.start_time != event.start_time) or \
       (event_in.end_time is not None and event_in.end_time != event.end_time):
        # Create EventCreate instance for conflict detection
        conflict_check = EventCreate(
            title=event_in.title if event_in.title is not None else event.title,
            description=event_in.description if event_in.description is not None else event.description,
            start_time=event_in.start_time if event_in.start_time is not None else event.start_time,
            end_time=event_in.end_time if event_in.end_time is not None else event.end_time,
            location=event_in.location if event_in.location is not None else event.location,
            is_recurring=event_in.is_recurring if event_in.is_recurring is not None else event.is_recurring,
            recurrence_pattern=event_in.recurrence_pattern if event_in.recurrence_pattern is not None else event.recurrence_pattern,
            recurrence_rule=event_in.recurrence_rule if event_in.recurrence_rule is not None else event.recurrence_rule
        )
        
        conflicts = EventService.detect_conflicts(db, conflict_check, current_user.id, event.id)
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Updated event conflicts with {len(conflicts)} existing events"
            )
    
    # Update the event
    updated_event = EventService.update_event(db, event, event_in, current_user)
    return updated_event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    *,
    db: Session = Depends(get_db),
    event: Event = Depends(lambda event_id, db=Depends(get_db), current_user=Depends(get_current_user): 
                            get_event_with_permission_check(event_id, current_user, "delete", db)),
) -> Any:
    """
    Delete an event.
    
    Args:
        db: Database session
        event: Event to delete (from dependency with permission check)
        
    Returns:
        None
    """
    EventService.delete_event(db, event)
    return None

@router.post("/batch", response_model=List[EventResponse], status_code=status.HTTP_201_CREATED)
def batch_create_events(
    *,
    db: Session = Depends(get_db),
    events_in: EventBatchCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create multiple events in a batch.
    
    Args:
        db: Database session
        events_in: Batch of events to create
        current_user: Current authenticated user
        
    Returns:
        List[EventResponse]: List of created events
    """
    # Check for conflicts in all events
    conflicts = []
    for event_in in events_in.events:
        event_conflicts = EventService.detect_conflicts(db, event_in, current_user.id)
        if event_conflicts:
            conflicts.append({
                "event": event_in,
                "conflicts": len(event_conflicts)
            })
    
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{len(conflicts)} events have conflicts"
        )
    
    # Create all events
    events = EventService.batch_create_events(db, events_in.events, current_user)
    return events

# ================== Collaboration Endpoints ==================

@router.post("/{event_id}/share", response_model=EventPermissionResponse)
def share_event(
    *,
    db: Session = Depends(get_db),
    event: Event = Depends(lambda event_id, db=Depends(get_db), current_user=Depends(get_current_user): 
                            get_event_with_permission_check(event_id, current_user, "manage", db)),
    permission_in: EventPermissionCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Share an event with another user.
    
    Args:
        db: Database session
        event: Event to share (from dependency with permission check)
        permission_in: Permission data
        current_user: Current authenticated user
        
    Returns:
        EventPermissionResponse: Created permission
        
    Raises:
        HTTPException: If user not found
    """
    # Check if user exists
    user = db.query(User).filter(User.id == permission_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Share the event
    permission = EventService.share_event(db, event, permission_in.user_id, permission_in.role)
    return permission

@router.get("/{event_id}/permissions", response_model=List[EventPermissionResponse])
def get_event_permissions(
    *,
    event: Event = Depends(lambda event_id, db=Depends(get_db), current_user=Depends(get_current_user): 
                            get_event_with_permission_check(event_id, current_user, "manage", db)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all permissions for an event.
    
    Args:
        event: Event (from dependency with permission check)
        db: Database session
        
    Returns:
        List[EventPermissionResponse]: List of permissions
    """
    permissions = EventService.get_event_permissions(db, event.id)
    return permissions

@router.put("/{event_id}/permissions/{user_id}", response_model=EventPermissionResponse)
def update_event_permission(
    *,
    event: Event = Depends(lambda event_id, db=Depends(get_db), current_user=Depends(get_current_user): 
                            get_event_with_permission_check(event_id, current_user, "manage", db)),
    user_id: int = Path(..., title="The ID of the user to update permissions for"),
    permission_in: EventPermissionUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a user's permission for an event.
    
    Args:
        event: Event (from dependency with permission check)
        user_id: User ID
        permission_in: Updated permission data
        db: Database session
        
    Returns:
        EventPermissionResponse: Updated permission
        
    Raises:
        HTTPException: If permission not found
    """
    permission = EventService.update_permission(db, event.id, user_id, permission_in.role)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission

@router.delete("/{event_id}/permissions/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event_permission(
    *,
    event: Event = Depends(lambda event_id, db=Depends(get_db), current_user=Depends(get_current_user): 
                            get_event_with_permission_check(event_id, current_user, "manage", db)),
    user_id: int = Path(..., title="The ID of the user to remove permissions for"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Remove a user's permission for an event.
    
    Args:
        event: Event (from dependency with permission check)
        user_id: User ID
        db: Database session
        
    Returns:
        None
        
    Raises:
        HTTPException: If permission not found
    """
    result = EventService.remove_permission(db, event.id, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return None

# ================== Version History Endpoints ==================

@router.get("/{event_id}/history/{version_id}", response_model=EventVersionDetailResponse)
def get_event_version(
    *,
    event: Event = Depends(lambda event_id, db=Depends(get_db), current_user=Depends(get_current_user): 
                            get_event_with_permission_check(event_id, current_user, "view", db)),
    version_id: int = Path(..., title="The version number to retrieve"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a specific version of an event.
    
    Args:
        event: Event (from dependency with permission check)
        version_id: Version number
        db: Database session
        
    Returns:
        EventVersionDetailResponse: Event version
        
    Raises:
        HTTPException: If version not found
    """
    version = EventService.get_event_version(db, event.id, version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    return version

@router.post("/{event_id}/rollback/{version_id}", response_model=EventResponse)
def rollback_event(
    *,
    event: Event = Depends(lambda event_id, db=Depends(get_db), current_user=Depends(get_current_user): 
                            get_event_with_permission_check(event_id, current_user, "edit", db)),
    version_id: int = Path(..., title="The version number to rollback to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Rollback an event to a previous version.
    
    Args:
        event: Event (from dependency with permission check)
        version_id: Version number to rollback to
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        EventResponse: Updated event
        
    Raises:
        HTTPException: If version not found
    """
    updated_event = EventService.rollback_event(db, event, version_id, current_user)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    return updated_event

@router.get("/{event_id}/changelog", response_model=List[EventVersionResponse])
def get_event_changelog(
    *,
    event: Event = Depends(lambda event_id, db=Depends(get_db), current_user=Depends(get_current_user): 
                            get_event_with_permission_check(event_id, current_user, "view", db)),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all versions of an event (changelog).
    
    Args:
        event: Event (from dependency with permission check)
        db: Database session
        
    Returns:
        List[EventVersionResponse]: List of event versions
    """
    versions = EventService.get_event_versions(db, event.id)
    return versions

@router.get("/{event_id}/diff/{version_id1}/{version_id2}", response_model=EventDiffResponse)
def get_event_diff(
    *,
    event: Event = Depends(lambda event_id, db=Depends(get_db), current_user=Depends(get_current_user): 
                            get_event_with_permission_check(event_id, current_user, "view", db)),
    version_id1: int = Path(..., title="First version number for comparison"),
    version_id2: int = Path(..., title="Second version number for comparison"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get differences between two event versions.
    
    Args:
        event: Event (from dependency with permission check)
        version_id1: First version number
        version_id2: Second version number
        db: Database session
        
    Returns:
        EventDiffResponse: Differences between versions
        
    Raises:
        HTTPException: If versions not found
    """
    diff = EventService.calculate_diff(db, event.id, version_id1, version_id2)
    if not diff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both versions not found"
        )
    
    return {
        "version1": version_id1,
        "version2": version_id2,
        "diff": diff
    }
