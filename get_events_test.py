from backend.app.database import get_connection


connection = get_connection()

events = connection.execute(
    """
    SELECT
        id,
        event_type,
        track_id,
        zone_id,
        risk_score,
        risk_level,
        status,
        video_timestamp
    FROM events
    ORDER BY id DESC
    LIMIT 5
    """
).fetchall()

print("Recent events:")

for event in events:
    print(dict(event))

connection.close()