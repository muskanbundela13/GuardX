import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.database import initialize_database
from backend.app.database import get_connection

from typing import Any

INCIDENT_STATUSES = {"OPEN", "ACKNOWLEDGED", "IN_PROGRESS", "RESOLVED", "CLOSED"}

def generate_incident_id():
    return f"INC-{uuid.uuid4().hex[:8].upper()}"

def event_response(row):
    """Return the stable, complete event shape used by list and detail APIs."""
    risk_level = row["risk_level"] or "LOW"
    return {
        "event_id": f"EVT-{row['id']:06d}",
        "database_id": row["id"],
        "event_type": row["event_type"],
        "risk_score": row["risk_score"] if row["risk_score"] is not None else 0,
        "risk_level": risk_level,
        "location": row["location"] or row["zone_id"],
        "camera_id": row["camera_id"],
        "detection_time": row["timestamp"],
        "timestamp": row["timestamp"],
        "video_timestamp": row["video_timestamp"],
        "frame_number": row["frame_number"],
        "confidence": row["confidence"],
        "track_id": row["track_id"],
        "zone_id": row["zone_id"],
        "session_id": row["session_id"],
        "video_file_id": row["video_file_id"],
        "incident_id": row["incident_id"],
        "incident_status": row["status"] or "OPEN",
        "status": row["status"] or "OPEN",
        "recommended_action": row["recommended_action"],
        "assigned_responder": row["assigned_responder"],
        "risk": {"risk_score": row["risk_score"] or 0, "risk_level": risk_level},
    }


def create_incident_for_event(connection, event_id: int, event: dict[str, Any], risk_score, risk_level):
    """Persist exactly one incident tied to a high-severity source event."""
    if (risk_level or "").upper() not in {"HIGH", "CRITICAL"}:
        return None

    existing = connection.execute(
        "SELECT incident_id FROM incidents WHERE related_event_ids = ?", (str(event_id),)
    ).fetchone()
    if existing:
        return existing["incident_id"]

    incident_id = generate_incident_id()
    connection.execute(
        """
        INSERT INTO incidents (
            incident_id, title, incident_type, priority, risk_score, risk_level,
            status, location, camera_id, zone_id, session_id, created_at,
            assigned_responder, related_event_ids, recommended_action
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            incident_id,
            event.get("event_type", event.get("type", "UNKNOWN")),
            event.get("event_type", event.get("type", "UNKNOWN")),
            risk_level,
            risk_score,
            risk_level,
            event.get("incident_status", event.get("status", "OPEN")),
            event.get("location"),
            event.get("camera_id"),
            event.get("zone_id"),
            event.get("session_id"),
            event.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            event.get("assigned_responder"),
            str(event_id),
            event.get("risk", {}).get("recommended_action", event.get("recommended_action")),
        ),
    )
    connection.execute("UPDATE events SET incident_id = ? WHERE id = ?", (incident_id, event_id))
    return incident_id


def backfill_incidents():
    """Create persisted incidents for high-severity events stored before this release."""
    connection = get_connection()
    rows = connection.execute(
        "SELECT * FROM events WHERE UPPER(COALESCE(risk_level, 'LOW')) IN ('HIGH', 'CRITICAL')"
    ).fetchall()
    for row in rows:
        create_incident_for_event(
            connection, row["id"], dict(row), row["risk_score"] or 0, row["risk_level"]
        )
    connection.commit()
    connection.close()


def load_events_from_database():
    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM events ORDER BY id"
    ).fetchall()

    connection.close()

    return [event_response(row) for row in rows]


def incident_query(where_clause: str = "", parameters: tuple = ()):
    connection = get_connection()
    rows = connection.execute(
        f"""
        SELECT incidents.*, events.id AS event_database_id, events.event_type AS source_event_type,
               events.track_id, events.zone_id AS event_zone_id, events.location AS event_location,
               events.video_timestamp, events.frame_number, events.session_id, events.video_file_id,
               events.camera_id AS event_camera_id, events.timestamp AS detection_time,
               events.confidence
        FROM incidents JOIN events ON incidents.related_event_ids = CAST(events.id AS TEXT)
        {where_clause}
        ORDER BY incidents.id
        """,
        parameters,
    ).fetchall()
    connection.close()
    return rows


def incident_response(row):
    return {
        "incident_id": row["incident_id"],
        "event_id": f"EVT-{row['event_database_id']:06d}",
        "database_id": row["event_database_id"],
        "event_type": row["source_event_type"],
        "track_id": row["track_id"],
        "zone_id": row["event_zone_id"] or row["zone_id"],
        "location": row["event_location"] or row["location"] or row["event_zone_id"],
        "camera_id": row["event_camera_id"] or row["camera_id"],
        "session_id": row["session_id"],
        "frame_number": row["frame_number"],
        "video_timestamp": row["video_timestamp"],
        "video_file_id": row["video_file_id"],
        "detection_time": row["detection_time"],
        "confidence": row["confidence"],
        "risk_score": row["risk_score"],
        "risk_level": row["risk_level"],
        "status": row["status"],
        "assigned_responder": row["assigned_responder"],
        "recommended_action": row["recommended_action"],
        "created_at": row["created_at"],
        "notes": row["notes"] or "",
    }

app = FastAPI(title="GuardX Backend")
initialize_database()
backfill_incidents()

events_store: list[dict[str, Any]] = []


@app.get("/api/events")
def get_events():
    return load_events_from_database()


@app.get("/api/events/{event_id}")
def get_event(event_id: str):
    """Fetch one live event. Unknown or malformed ids return a proper 404."""
    raw_id = event_id.removeprefix("EVT-")
    try:
        database_id = int(raw_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Event not found") from error

    connection = get_connection()
    row = connection.execute("SELECT * FROM events WHERE id = ?", (database_id,)).fetchone()
    connection.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event_response(row)

@app.post("/api/events")
def add_event(event: dict[str, Any]):
    risk = event.get("risk", {})

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO events (
            event_type,
            track_id,
            zone_id,
            timestamp,
            confidence,
            risk_score,
            risk_level,
            status,
            assigned_responder,
            video_timestamp, camera_id, location, frame_number, session_id, video_file_id,
            incident_id, recommended_action
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.get("event_type", event.get("type", "UNKNOWN")),
            event.get("track_id"),
            event.get("zone_id"),
            event.get("timestamp"),
            event.get("confidence"),
            risk.get("risk_score", event.get("reliability_score", 0)),
            risk.get("risk_level", event.get("risk_level", "LOW")),
            event.get("incident_status", event.get("status", "OPEN")),
            event.get("assigned_responder"),
            event.get("video_timestamp"),
            event.get("camera_id"),
            event.get("location"),
            event.get("frame_number", event.get("current_frame")),
            event.get("session_id"),
            event.get("video_file_id"),
            event.get("incident_id"),
            risk.get("recommended_action", event.get("recommended_action")),
        ),
    )

    risk_score = risk.get("risk_score", event.get("reliability_score", 0))
    risk_level = risk.get("risk_level", event.get("risk_level", "LOW"))
    incident_id = create_incident_for_event(connection, cursor.lastrowid, event, risk_score, risk_level)
    connection.commit()
    event["database_id"] = cursor.lastrowid
    event["event_id"] = f"EVT-{cursor.lastrowid:06d}"
    event["incident_id"] = incident_id
    connection.close()

    events_store.append(event)

    return {
        "status": "success",
        "event": event
    }

@app.get("/api/analytics")
def get_analytics():
    events_store = load_events_from_database()
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

    # Threat-level distribution
    threat_distribution = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }

    # Event-type distribution
    event_type_distribution = {}

    for event in events_store:
        risk = event.get("risk", {})
        risk_level = risk.get("risk_level", "LOW")

        if risk_level not in threat_distribution:
            risk_level = "LOW"

        threat_distribution[risk_level] += 1

        event_type = event.get(
            "event_type",
            event.get("type", "UNKNOWN")
        )

        event_type_distribution[event_type] = (
            event_type_distribution.get(event_type, 0) + 1
        )

    return {
        "total_events": total_events,
        "average_risk": round(average_risk, 1),
        "high_risk_events": high_risk_events,
        "threat_distribution": threat_distribution,
        "event_type_distribution": event_type_distribution,
    }


@app.get("/api/incidents")
def get_incidents():
    return [incident_response(row) for row in incident_query()]


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    rows = incident_query("WHERE incidents.incident_id = ?", (incident_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident_response(rows[0])


class IncidentUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


@app.patch("/api/incidents/{incident_id}")
def update_incident(incident_id: str, update: IncidentUpdate):
    changes = update.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Provide status and/or notes")

    if "status" in changes:
        changes["status"] = changes["status"].upper()
        if changes["status"] not in INCIDENT_STATUSES:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status. Use one of: {', '.join(sorted(INCIDENT_STATUSES))}",
            )

    connection = get_connection()
    incident = connection.execute(
        "SELECT related_event_ids FROM incidents WHERE incident_id = ?", (incident_id,)
    ).fetchone()
    if incident is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Incident not found")

    assignments = ", ".join(f"{field} = ?" for field in changes)
    connection.execute(
        f"UPDATE incidents SET {assignments} WHERE incident_id = ?",
        (*changes.values(), incident_id),
    )
    # Incident status is mirrored to its one source event; notes never touch event data.
    if "status" in changes:
        connection.execute(
            "UPDATE events SET status = ? WHERE id = ?",
            (changes["status"], int(incident["related_event_ids"])),
        )
    connection.commit()
    connection.close()
    return get_incident(incident_id)

@app.post("/api/incidents/{incident_id}/assign")
def assign_incident(incident_id: str, assignment: dict[str, Any]):
    responder_id = assignment.get("responder_id")

    valid_responder_ids = {
        "RESP-001",
        "RESP-002",
        "RESP-003",
        "RESP-004",
    }

    if not responder_id:
        return {
            "status": "error",
            "message": "responder_id is required"
        }

    if responder_id not in valid_responder_ids:
        return {
            "status": "error",
            "message": "Invalid responder_id"
        }

    connection = get_connection()
    incident = connection.execute(
        "SELECT related_event_ids FROM incidents WHERE incident_id = ?", (incident_id,)
    ).fetchone()
    if incident is None:
        connection.close()
        return {"status": "error", "message": "Incident not found"}
    event_id = int(incident["related_event_ids"])
    cursor = connection.execute(
        "UPDATE incidents SET assigned_responder = ?, status = ? WHERE incident_id = ?",
        (responder_id, "IN_PROGRESS", incident_id),
    )
    connection.execute("UPDATE events SET assigned_responder = ?, status = ? WHERE id = ?", (responder_id, "IN_PROGRESS", event_id))

    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        return {
            "status": "error",
            "message": "Incident not found"
        }

    return {
        "status": "success",
        "incident_id": incident_id,
        "assigned_responder": responder_id,
        "incident_status": "IN_PROGRESS"
    }

@app.patch("/api/incidents/{incident_id}/status")
def update_incident_status(
    incident_id: str,
    status_update: dict[str, Any]
):
    new_status = status_update.get("status")

    allowed_statuses = INCIDENT_STATUSES

    if new_status not in allowed_statuses:
        raise HTTPException(status_code=422, detail="Invalid incident status")

    connection = get_connection()
    incident = connection.execute(
        "SELECT related_event_ids FROM incidents WHERE incident_id = ?", (incident_id,)
    ).fetchone()
    if incident is None:
        connection.close()
        return {"status": "error", "message": "Incident not found"}
    event_id = int(incident["related_event_ids"])
    cursor = connection.execute("UPDATE incidents SET status = ? WHERE incident_id = ?", (new_status, incident_id))
    connection.execute("UPDATE events SET status = ? WHERE id = ?", (new_status, event_id))

    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        return {
            "status": "error",
            "message": "Incident not found"
        }

    return {
        "status": "success",
        "incident_id": incident_id,
        "incident_status": new_status
    }

@app.get("/api/incidents/stats")
def get_incident_stats():

    events_store = load_events_from_database()

    total_incidents = 0
    open_incidents = 0
    assigned_incidents = 0
    resolved_incidents = 0
    high_risk_incidents = 0

    for event in events_store:
        risk = event.get("risk", {})
        risk_level = risk.get("risk_level", "LOW")

        if risk_level not in {"HIGH", "CRITICAL"} and event.get(
            "reliability_score", 0
        ) < 70:
            continue

        total_incidents += 1

        status = event.get("status", "OPEN")

        if status == "OPEN":
            open_incidents += 1
        elif status == "ASSIGNED":
            assigned_incidents += 1
        elif status == "RESOLVED":
            resolved_incidents += 1

        if risk_level in {"HIGH", "CRITICAL"}:
            high_risk_incidents += 1

    return {
        "total_incidents": total_incidents,
        "open_incidents": open_incidents,
        "assigned_incidents": assigned_incidents,
        "resolved_incidents": resolved_incidents,
        "high_risk_incidents": high_risk_incidents,
    }

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
