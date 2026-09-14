from backend.app.database import get_connection
from datetime import datetime


connection = get_connection()

event = {
    "event_type": "INTRUSION",
    "track_id": 101,
    "zone_id": "ZONE-A",
    "timestamp": datetime.now().isoformat(),
    "confidence": 0.95,
    "risk_score": 85.0,
    "risk_level": "HIGH",
    "status": "OPEN",
    "assigned_responder": None,
    "video_timestamp": 12.5,
}

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
        video_timestamp
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        event["event_type"],
        event["track_id"],
        event["zone_id"],
        event["timestamp"],
        event["confidence"],
        event["risk_score"],
        event["risk_level"],
        event["status"],
        event["assigned_responder"],
        event["video_timestamp"],
    ),
)

connection.commit()

event_id = cursor.lastrowid

saved_event = connection.execute(
    "SELECT * FROM events WHERE id = ?",
    (event_id,),
).fetchone()

print("Inserted event:", dict(saved_event))

connection.close()