import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from risk.risk_engine import risk_engine
from risk.response_engine import response_engine
from api.event_deduplicator import event_deduplicator
from api.event_store import event_store

from risk.context_engine import context_engine
from risk.simulator import response_simulator


router = APIRouter(
    tags=["GuardX Backend"]
)


class CVEventRequest(BaseModel):
    event_type: str = Field(..., min_length=1)
    timestamp: float
    track_id: Optional[int] = None
    zone: Optional[str] = None
    confidence: Optional[float] = None
    reliability_score: Optional[float] = None

    details: Dict[str, Any] = Field(default_factory=dict)
    time_anomaly: Optional[float] = None
    zone_sensitivity: Optional[float] = None
    crowd_anomaly: Optional[float] = None
    access_violation: Optional[float] = None
    predicted_baseline_risk: Optional[float] = None

    details: Dict[str, Any] = Field(default_factory=dict)

class CVEventResponse(BaseModel):
    status: str
    message: str
    event: Dict[str, Any]
    risk: Dict[str, Any]
    response: Dict[str, Any]
    total_events_received: int


def process_cv_event(event: CVEventRequest):
    if event.reliability_score is not None:
        if not 0 <= event.reliability_score <= 100:
            raise HTTPException(
                status_code=400,
                detail="reliability_score must be between 0 and 100",
            )

    if event.confidence is not None:
        if not 0 <= event.confidence <= 1:
            raise HTTPException(
                status_code=400,
                detail="confidence must be between 0 and 1",
            )

    event_data = event.model_dump()

    context_data = context_engine.build_context(event_data)
    event_data.update(context_data)

    event_data["event_id"] = str(uuid.uuid4())
    event_data["received_at"] = datetime.now(timezone.utc).isoformat()

    event_data["evidence"] = {
        "source": "GuardX CV pipeline",
        "frame_number": event_data["details"].get("frame_number"),
        "video_timestamp": event_data["timestamp"],
        "evidence_path": event_data["details"].get("evidence_path"),
        "privacy_mode": "no_face_recognition",
        "temporary_tracking_only": True,
    }

    if not event_deduplicator.should_accept(event_data):
        return {
            "status": "ignored",
            "message": "Duplicate event ignored during cooldown",
            "event": event_data,
            "risk": {},
            "response": {},
            "total_events_received": event_store.get_event_count(),
        }

    risk_result = risk_engine.calculate_risk(event_data)
    response_result = response_engine.decide(risk_result)

    event_data["risk"] = risk_result
    event_data["response"] = response_result

    event_store.add_event(event_data)

    return {
        "status": "success",
        "message": "CV event received successfully",
        "event": event_data,
        "risk": risk_result,
        "response": response_result,
        "total_events_received": event_store.get_event_count(),
    }


# Existing Member 1 endpoint
@router.post("/api/events/ingest", response_model=CVEventResponse)
def ingest_cv_event(event: CVEventRequest):
    return process_cv_event(event)


# Member 2 endpoint
@router.post("/api/detect")
def detect_event(event: CVEventRequest):
    return process_cv_event(event)


@router.get("/api/events")
def get_received_events():
    return {
        "status": "success",
        "total_events": event_store.get_event_count(),
        "events": event_store.get_events(),
    }


@router.delete("/api/events")
def clear_received_events():
    event_store.clear_events()

    return {
        "status": "success",
        "message": "Received CV events cleared",
    }


@router.get("/api/incidents")
def get_incidents():
    return {
        "status": "success",
        "total_incidents": event_store.get_event_count(),
        "incidents": event_store.get_events(),
    }


@router.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    for event in event_store.get_events():
        if event.get("event_id") == incident_id:
            return {
                "status": "success",
                "incident": event,
            }

    raise HTTPException(
        status_code=404,
        detail="Incident not found",
    )


@router.post("/api/risk/calculate")
def calculate_risk(payload: Dict[str, Any]):
    return {
        "status": "pending",
        "message": "Risk calculation endpoint is ready",
        "input": payload,
    }


@router.post("/api/simulate")
def simulate_response(payload: Dict[str, Any]):
    current_risk = payload.get("current_risk")

    if current_risk is None:
        return {
            "status": "error",
            "message": "current_risk is required",
        }

    try:
        current_risk = float(current_risk)
    except (TypeError, ValueError):
        return {
            "status": "error",
            "message": "current_risk must be numeric",
        }

    current_risk = max(0, min(100, current_risk))

    strategy = payload.get("strategy")

    if strategy:
        return response_simulator.simulate(
            current_risk,
            strategy
        )

    return response_simulator.compare_strategies(
        current_risk
    )


@router.post("/api/recommend")
def recommend_response(payload: Dict[str, Any]):
    return {
        "status": "pending",
        "message": "Response optimizer will be connected later",
        "input": payload,
    }


@router.get("/api/responders")
def get_responders():
    return {
        "status": "success",
        "responders": [],
    }


@router.get("/api/map")
def get_map_data():
    return {
        "status": "success",
        "zones": [],
    }


@router.get("/api/analytics")
def get_analytics():
    events = event_store.get_events()

    risk_distribution = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0,
    }

    for event in events:
        risk_level = event.get("risk", {}).get("risk_level")

        if risk_level in risk_distribution:
            risk_distribution[risk_level] += 1

    return {
        "status": "success",
        "total_events": len(events),
        "risk_distribution": risk_distribution,
    }


@router.get("/api/heatmap")
def get_heatmap():
    return {
        "status": "success",
        "heatmap": [],
    }


@router.get("/api/patrol-route")
def get_patrol_route():
    return {
        "status": "success",
        "route": [],
    }


@router.get("/api/events/calendar")
def get_calendar_events():
    return {
        "status": "success",
        "events": event_store.get_events(),
    }