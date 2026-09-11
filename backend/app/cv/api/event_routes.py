from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.event_store import event_store


router = APIRouter(
    prefix="/api/events",
    tags=["CV Events"]
)


class CVEventRequest(BaseModel):
    event_type: str = Field(..., min_length=1)
    timestamp: float
    track_id: Optional[int] = None
    zone: Optional[str] = None
    confidence: Optional[float] = None
    reliability_score: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class CVEventResponse(BaseModel):
    status: str
    message: str
    event: CVEventRequest
    total_events_received: int


@router.post(
    "/ingest",
    response_model=CVEventResponse
)
def ingest_cv_event(event: CVEventRequest):

    if event.reliability_score is not None:
        if not 0 <= event.reliability_score <= 100:
            raise HTTPException(
                status_code=400,
                detail="reliability_score must be between 0 and 100"
            )

    if event.confidence is not None:
        if not 0 <= event.confidence <= 1:
            raise HTTPException(
                status_code=400,
                detail="confidence must be between 0 and 1"
            )

    event_data = event.model_dump()

    event_store.add_event(event_data)

    return CVEventResponse(
        status="success",
        message="CV event received successfully",
        event=event,
        total_events_received=event_store.get_event_count()
    )


@router.get("")
def get_received_events():

    return {
        "status": "success",
        "total_events": event_store.get_event_count(),
        "events": event_store.get_events()
    }


@router.delete("")
def clear_received_events():

    event_store.clear_events()

    return {
        "status": "success",
        "message": "Received CV events cleared"
    }