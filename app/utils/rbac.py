"""
Role-based access control utilities.

This module provides helper functions for handling permissions and access control.
"""

from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.user import User, UserRole
from app.schemas.event import Event, EventPermission
from app.api.v1.endpoints.auth import get_current_user


class RoleChecker:
    """
    RBAC utility class for checking event-related permissions.
    
    Permissions hierarchy (higher roles include lower roles' permissions):
    - OWNER: Full control (create, read, update, delete, share)
    - EDITOR: Modify event details (read, update)
    - VIEWER: View only (read)
    """
    
    @staticmethod
    def is_event_owner(user_id: int, event: Event) -> bool:
        """Check if user is the owner of the event."""
        return event.owner_id == user_id
    
    @staticmethod
    def get_user_role_for_event(user_id: int, event: Event) -> Optional[UserRole]:
        """Get the user's role for an event."""
        if RoleChecker.is_event_owner(user_id, event):
            return UserRole.OWNER
            
        for permission in event.permissions:
            if permission.user_id == user_id:
                return permission.role
                
        return None
    
    @staticmethod
    def can_view_event(user_id: int, event: Event) -> bool:
        """Check if user can view an event."""
        role = RoleChecker.get_user_role_for_event(user_id, event)
        return role is not None  # Any role (OWNER, EDITOR, VIEWER) can view
    
    @staticmethod
    def can_edit_event(user_id: int, event: Event) -> bool:
        """Check if user can edit an event."""
        role = RoleChecker.get_user_role_for_event(user_id, event)
        return role in [UserRole.OWNER, UserRole.EDITOR]
    
    @staticmethod
    def can_delete_event(user_id: int, event: Event) -> bool:
        """Check if user can delete an event."""
        return RoleChecker.is_event_owner(user_id, event)
    
    @staticmethod
    def can_manage_permissions(user_id: int, event: Event) -> bool:
        """Check if user can manage event permissions (share with others)."""
        return RoleChecker.is_event_owner(user_id, event)


def get_event_with_permission_check(
    event_id: int, 
    current_user: User = Depends(get_current_user),
    permission_type: str = "view",
    db: Session = Depends(get_db),
) -> Event:
    """
    Get an event with permission check.
    
    Args:
        event_id: ID of the event to retrieve
        current_user: Current authenticated user
        permission_type: Type of permission required (view, edit, delete, manage)
        db: Database session
        
    Returns:
        Event: The requested event
        
    Raises:
        HTTPException: If event not found or permission denied
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    has_permission = False
    
    if permission_type == "view":
        has_permission = RoleChecker.can_view_event(current_user.id, event)
    elif permission_type == "edit":
        has_permission = RoleChecker.can_edit_event(current_user.id, event)
    elif permission_type == "delete":
        has_permission = RoleChecker.can_delete_event(current_user.id, event)
    elif permission_type == "manage":
        has_permission = RoleChecker.can_manage_permissions(current_user.id, event)
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions to {permission_type} this event"
        )
    
    return event
