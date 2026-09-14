from datetime import datetime, timezone

from backend.app.database import get_connection
from backend.app.main import generate_incident_id


incident_id = generate_incident_id()

connection = get_connection()

connection.execute(
    """
    INSERT INTO incidents (
        incident_id,
        title,
        incident_type,
        priority,
        risk_score,
        risk_level,
        status,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        incident_id,
        "Test Security Incident",
        "TEST_EVENT",
        "HIGH",
        85.0,
        "HIGH",
        "NEW",
        datetime.now(timezone.utc).isoformat(),
    ),
)

connection.commit()

print("Inserted incident:", incident_id)

row = connection.execute(
    """
    SELECT incident_id, title, priority, risk_score, risk_level, status
    FROM incidents
    WHERE incident_id = ?
    """,
    (incident_id,),
).fetchone()

print("Retrieved incident:", dict(row))

connection.close()