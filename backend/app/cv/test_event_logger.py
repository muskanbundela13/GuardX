import time

from event_schema import SecurityEvent
from event_logger import EventLogger


logger = EventLogger("test_events.jsonl")

event = SecurityEvent(
    event_type="RESTRICTED_ZONE_ENTRY",
    timestamp=time.time(),
    track_id=1,
    zone="restricted_area",
    confidence=0.9
)

logger.log(event)

print("Logged Events:")
print(logger.get_events())

logger.clear()

print("\nAfter Clear:")
print(logger.get_events())