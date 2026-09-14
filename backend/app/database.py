import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "guardx.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            track_id INTEGER,
            zone_id TEXT,
            timestamp TEXT,
            confidence REAL,
            risk_score REAL,
            risk_level TEXT,
            status TEXT DEFAULT 'OPEN',
            assigned_responder TEXT,
            video_timestamp REAL,
            camera_id TEXT,
            location TEXT,
            frame_number INTEGER,
            session_id TEXT,
            video_file_id TEXT,
            incident_id TEXT,
            recommended_action TEXT
        )
    """)

    # Keep existing local databases compatible as the event payload grows.
    for column, definition in (
        ("video_timestamp", "REAL"),
        ("camera_id", "TEXT"),
        ("location", "TEXT"),
        ("frame_number", "INTEGER"),
        ("session_id", "TEXT"),
        ("video_file_id", "TEXT"),
        ("incident_id", "TEXT"),
        ("recommended_action", "TEXT"),
    ):
        try:
            connection.execute(f"ALTER TABLE events ADD COLUMN {column} {definition}")
        except sqlite3.OperationalError as error:
            if "duplicate column name" not in str(error).lower():
                raise

    connection.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            priority TEXT NOT NULL,
            risk_score REAL NOT NULL,
            risk_level TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN',
            location TEXT,
            camera_id TEXT,
            zone_id TEXT,
            session_id TEXT,
            created_at TEXT NOT NULL,
            acknowledged_at TEXT,
            assigned_at TEXT,
            resolved_at TEXT,
            closed_at TEXT,
            assigned_responder TEXT,
            related_event_ids TEXT,
            status_history TEXT,
            recommended_action TEXT,
            notes TEXT DEFAULT ''
        )
    """)

    try:
        connection.execute(
            "UPDATE incidents SET status = 'OPEN' WHERE status = 'NEW'"
        )
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()
