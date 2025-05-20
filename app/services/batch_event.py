"""Batch event operations service."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.event import Event
from app.schemas.event import EventCreate, EventResponse
from app.services.event import EventService
from app.core.exceptions import BatchOperationError

class BatchEventService:
    """Service for handling batch operations on events."""

    @staticmethod
    async def create_batch_events(
        db: Session,
        events_data: List[EventCreate],
        current_user_id: int,
        max_batch_size: int = 100
    ) -> List[EventResponse]:
        """
        Create multiple events in a single transaction.
        
        Args:
            db: Database session
            events_data: List of event data
            current_user_id: ID of the user creating events
            max_batch_size: Maximum number of events in one batch
            
        Returns:
            List of created events
            
        Raises:
            BatchOperationError: If batch creation fails
        """
        if len(events_data) > max_batch_size:
            raise BatchOperationError(
                f"Batch size exceeds maximum limit of {max_batch_size}"
            )
        
        created_events = []
        
        try:
            # Start transaction
            for event_data in events_data:
                event = await EventService.create_event(
                    db=db,
                    event_in=event_data,
                    current_user_id=current_user_id
                )
                created_events.append(event)
                
            db.commit()
            return created_events
            
        except Exception as e:
            db.rollback()
            raise BatchOperationError(f"Batch creation failed: {str(e)}")

    @staticmethod
    async def validate_batch_request(
        events_data: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Validate batch request data.
        
        Args:
            events_data: List of event data to validate
            
        Returns:
            Error message if validation fails, None otherwise
        """
        if not events_data:
            return "Empty batch request"
            
        for idx, event in enumerate(events_data):
            if not all(k in event for k in ("title", "start_time", "end_time")):
                return f"Missing required fields in event at index {idx}"
                
        return None
