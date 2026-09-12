import time

from app.cv.event_schema import SecurityEvent
from app.cv.event_reliability import EventReliability
from app.cv.event_manager import EventManager
from app.cv.cv_event_output import CVEventOutput


event_reliability = EventReliability(
    cooldown_seconds=0
)

event_manager = EventManager()
cv_event_output = CVEventOutput()


event = SecurityEvent(
    event_type="RESTRICTED_ZONE_ENTRY",
    timestamp=time.time(),
    track_id=101,
    zone="restricted_area",
    confidence=0.95,
    details={
        "source": "cv"
    }
)


print("Original Event:")
print(event.to_dict())


reliable = event_reliability.is_reliable(event)

assert reliable is True

print("\nReliability Check:")
print("PASSED")


stored_event = event_manager.process_event(event)

assert stored_event is not None

print("\nEventManager:")
print(stored_event.to_dict())


backend_event = cv_event_output.publish(
    stored_event
)

assert backend_event is not None

print("\nBackend-Ready Event:")
print(backend_event)


assert backend_event["event_type"] == (
    "RESTRICTED_ZONE_ENTRY"
)

assert backend_event["track_id"] == 101

assert backend_event["zone"] == (
    "restricted_area"
)

assert backend_event["reliability_score"] == 95.0

assert len(
    cv_event_output.get_outputs()
) == 1


print("\nCV pipeline handoff test passed.")