from app.cv.event_manager import EventManager
from app.cv.event_schema import SecurityEvent


def test_manager_stores_valid_security_event():
    manager = EventManager()

    event = SecurityEvent(
        event_type="RESTRICTED_ZONE_ENTRY",
        timestamp=1000,
        track_id=43,
        zone="restricted_area",
        confidence=0.95,
    )

    result = manager.process_event(event)

    assert result is event
    assert len(manager.get_events()) == 1


def test_manager_rejects_invalid_security_event():
    manager = EventManager()

    event = SecurityEvent(
        event_type="RESTRICTED_ZONE_ENTRY",
        timestamp=1000,
        track_id=None,
        zone="restricted_area",
        confidence=0.95,
    )

    result = manager.process_event(event)

    assert result is None
    assert manager.get_events() == []


def test_manager_rejects_none_event():
    manager = EventManager()

    result = manager.process_event(None)

    assert result is None
    assert manager.get_events() == []