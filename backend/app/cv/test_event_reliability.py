import time

from event_schema import SecurityEvent
from event_reliability import EventReliability


reliability = EventReliability(confidence_threshold=0.5)


valid_event = SecurityEvent(
    event_type="RESTRICTED_ZONE_ENTRY",
    timestamp=time.time(),
    track_id=1,
    zone="restricted_area",
    confidence=0.9
)

low_confidence_event = SecurityEvent(
    event_type="RESTRICTED_ZONE_ENTRY",
    timestamp=time.time(),
    track_id=2,
    zone="restricted_area",
    confidence=0.3
)

print("Valid Event:")
print(reliability.is_reliable(valid_event))

print("\nDuplicate Event:")
print(reliability.is_reliable(valid_event))

print("\nLow Confidence Event:")
print(reliability.is_reliable(low_confidence_event))