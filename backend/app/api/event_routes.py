import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from risk.risk_engine import risk_engine
from risk.response_engine import response_engine
from api.event_deduplicator import event_deduplicator
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
    event: Dict[str, Any]
    risk: Dict[str, Any]
    response: Dict[str, Any]
    total_events_received: int


@router.post("/ingest", response_model=CVEventResponse)
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

    event_data["event_id"] = str(uuid.uuid4())

    event_data["received_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    event_data["evidence"] = {
        "source": "GuardX CV pipeline",
        "frame_number": event_data.get(
            "details",
            {}
        ).get("frame_number"),
        "video_timestamp": event_data.get("timestamp"),
        "evidence_path": event_data.get(
            "details",
            {}
        ).get("evidence_path"),
        "privacy_mode": "no_face_recognition",
        "temporary_tracking_only": True
    }

    if not event_deduplicator.should_accept(event_data):
        return {
            "status": "ignored",
            "message": "Duplicate event ignored during cooldown",
            "event": event_data,
            "risk": {},
            "response": {},
            "total_events_received": event_store.get_event_count()
        }

    risk_result = risk_engine.calculate_risk(event_data)

    response_result = response_engine.decide(
        risk_result
    )

    event_data["risk"] = risk_result
    event_data["response"] = response_result

    event_store.add_event(event_data)

    return {
        "status": "success",
        "message": "CV event received successfully",
        "event": event_data,
        "risk": risk_result,
        "response": response_result,
        "total_events_received": event_store.get_event_count()
    }


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