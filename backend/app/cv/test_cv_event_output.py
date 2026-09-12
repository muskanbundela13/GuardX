from app.cv.cv_event_output import CVEventOutput
from app.cv.event_schema import SecurityEvent


def test_create_output_from_valid_event():
    event = SecurityEvent(
        event_type="RESTRICTED_ZONE_ENTRY",
        timestamp=1000,
        track_id=43,
        zone="restricted_area",
        confidence=0.95,
        details={"reliability_score": 0.88},
    )

    output_system = CVEventOutput()
    output = output_system.create_output(event)

    assert output is not None
    assert output["event_type"] == "RESTRICTED_ZONE_ENTRY"
    assert output["timestamp"] == 1000
    assert output["track_id"] == 43
    assert output["zone"] == "restricted_area"
    assert output["confidence"] == 0.95
    assert output["reliability_score"] == 0.88


def test_create_output_rejects_invalid_object():
    output_system = CVEventOutput()

    output = output_system.create_output(
        {"event_type": "CROWD_ANOMALY"}
    )

    assert output is None


def test_publish_stores_output():
    event = SecurityEvent(
        event_type="CROWD_ANOMALY",
        timestamp=1001,
        track_id=12,
        zone="main_gate",
        confidence=0.90,
    )

    output_system = CVEventOutput()
    output = output_system.publish(event)

    assert output is not None
    assert len(output_system.get_outputs()) == 1
    assert output_system.get_outputs()[0]["event_type"] == "CROWD_ANOMALY"


def test_clear_removes_outputs():
    event = SecurityEvent(
        event_type="CROWD_ANOMALY",
        timestamp=1001,
    )

    output_system = CVEventOutput()
    output_system.publish(event)

    output_system.clear()

    assert output_system.get_outputs() == []