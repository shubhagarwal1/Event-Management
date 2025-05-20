"""Batch events endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.event import EventCreate, EventResponse
from app.services.batch_event import BatchEventService
from app.core.exceptions import BatchOperationError

router = APIRouter()

@router.post("/batch", response_model=List[EventResponse], status_code=201)
async def create_batch_events(
    *,
    db: Session = Depends(deps.get_db),
    events_in: List[EventCreate],
    current_user = Depends(deps.get_current_user)
) -> List[EventResponse]:
    """
    Create multiple events in a single request.
    
    Args:
        db: Database session
        events_in: List of events to create
        current_user: Current authenticated user
        
    Returns:
        List of created events
        
    Raises:
        HTTPException: If batch creation fails
    """
    try:
        # Validate batch request
        error = await BatchEventService.validate_batch_request(
            [event.dict() for event in events_in]
        )
        if error:
            raise HTTPException(status_code=400, detail=error)
            
        # Create events in batch
        events = await BatchEventService.create_batch_events(
            db=db,
            events_data=events_in,
            current_user_id=current_user.id
        )
        return events
        
    except BatchOperationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
