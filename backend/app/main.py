from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from typing import Any

app = FastAPI(title="GuardX Backend")

events_store: list[dict[str, Any]] = []


@app.get("/api/events")
def get_events():
    return events_store

@app.post("/api/events")
def add_event(event: dict[str, Any]):
    events_store.append(event)
    return {
        "status": "success",
        "event": event,
    }

@app.get("/api/analytics")
def get_analytics():
    total_events = len(events_store)

    risk_scores = [
        event.get("risk", {}).get(
            "risk_score",
            event.get("reliability_score", 0)
        )
        for event in events_store
    ]

    average_risk = (
        sum(risk_scores) / len(risk_scores)
        if risk_scores
        else 0
    )

    high_risk_events = sum(
        1
        for event in events_store
        if event.get("risk", {}).get("risk_level") == "HIGH"
        or event.get("reliability_score", 0) >= 70
    )

    return {
        "total_events": total_events,
        "average_risk": round(average_risk, 1),
        "high_risk_events": high_risk_events,
    }


@app.get("/api/incidents")
def get_incidents():
    return [
        event
        for event in events_store
        if (
            event.get("risk", {}).get("risk_level") in {"HIGH", "CRITICAL"}
            or event.get("reliability_score", 0) >= 70
        )
    ]


@app.get("/api/responders")
def get_responders():
    return [
        {
            "id": "RESP-001",
            "name": "Security Team",
            "status": "AVAILABLE",
        },
        {
            "id": "RESP-002",
            "name": "Campus Patrol",
            "status": "AVAILABLE",
        },
        {
            "id": "RESP-003",
            "name": "Control Room",
            "status": "AVAILABLE",
        },
        {
            "id": "RESP-004",
            "name": "Emergency Response",
            "status": "AVAILABLE",
        },
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


VIDEO_PATH = (
    Path(__file__).resolve().parents[2]
    / "demo"
    / "istockphoto-1995820194-640_adpp_is.mp4"
)


class VideoSession:
    def __init__(self):
        self.session_id = None
        self.status = "IDLE"
        self.video_name = VIDEO_PATH.name
        self.video_path = str(VIDEO_PATH)
        self.started_at = None
        self.stopped_at = None
        self.current_time = 0.0
        self.duration = 0.0
        self.current_frame = 0
        self.completed = False


video_session = VideoSession()
session_lock = Lock()


def session_response():
    return {
        "status": "success",
        "session": {
            "session_id": video_session.session_id,
            "status": video_session.status,
            "video_name": video_session.video_name,
            "video_path": video_session.video_path,
            "started_at": video_session.started_at,
            "stopped_at": video_session.stopped_at,
            "current_time": video_session.current_time,
            "duration": video_session.duration,
            "current_frame": video_session.current_frame,
            "completed": video_session.completed,
        },
    }


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "GuardX backend is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "GuardX Backend",
    }


@app.get("/api/video/session")
def get_video_session():
    with session_lock:
        return session_response()


@app.post("/api/video/start")
def start_video_session():
    with session_lock:
        if not VIDEO_PATH.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Video file not found: {VIDEO_PATH}",
            )

        video_session.session_id = str(uuid4())
        video_session.status = "RUNNING"
        video_session.started_at = datetime.now(
            timezone.utc
        ).isoformat()
        video_session.stopped_at = None
        video_session.current_time = 0.0
        video_session.duration = 0.0
        video_session.current_frame = 0
        video_session.completed = False

        return session_response()


@app.post("/api/video/stop")
def stop_video_session():
    with session_lock:
        if video_session.session_id is None:
            raise HTTPException(
                status_code=400,
                detail="No active video session",
            )

        video_session.status = "STOPPED"
        video_session.stopped_at = datetime.now(
            timezone.utc
        ).isoformat()

        return session_response()


@app.post("/api/video/reset")
def reset_video_session():
    with session_lock:
        video_session.session_id = None
        video_session.status = "IDLE"
        video_session.started_at = None
        video_session.stopped_at = None
        video_session.current_time = 0.0
        video_session.duration = 0.0
        video_session.current_frame = 0
        video_session.completed = False

        return session_response()


class VideoProgress(BaseModel):
    current_time: float = 0.0
    duration: float = 0.0
    current_frame: int = 0
    completed: bool = False


@app.post("/api/video/progress")
def update_video_progress(progress: VideoProgress):
    with session_lock:
        if video_session.session_id is None:
            raise HTTPException(
                status_code=400,
                detail="No active video session",
            )

        video_session.current_time = max(
            0.0,
            progress.current_time,
        )
        video_session.duration = max(
            0.0,
            progress.duration,
        )
        video_session.current_frame = max(
            0,
            progress.current_frame,
        )
        video_session.completed = progress.completed

        if progress.completed:
            video_session.status = "COMPLETED"

        return session_response()