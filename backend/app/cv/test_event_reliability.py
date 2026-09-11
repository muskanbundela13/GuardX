import time

from event_reliability import EventReliability
from event_schema import SecurityEvent


reliability = EventReliability()


valid_event = SecurityEvent(
    event_type="RESTRICTED_ZONE_ENTRY",
    timestamp=time.time(),
    track_id=101,
    zone="restricted_area",
    confidence=0.9
)

print("Valid Event:")
print(reliability.is_reliable(valid_event))

print("Reliability Score:")
print(valid_event.details)

assert valid_event.details["reliability_score"] == 90.0


duplicate_event = SecurityEvent(
    event_type="RESTRICTED_ZONE_ENTRY",
    timestamp=time.time(),
    track_id=101,
    zone="restricted_area",
    confidence=0.9
)

duplicate_result = reliability.is_reliable(duplicate_event)

print("\nDuplicate Event:")
print(duplicate_result)

assert duplicate_result is False


low_confidence_event = SecurityEvent(
    event_type="RESTRICTED_ZONE_ENTRY",
    timestamp=time.time(),
    track_id=102,
    zone="restricted_area",
    confidence=0.2
)

low_confidence_result = reliability.is_reliable(
    low_confidence_event
)

print("\nLow Confidence Event:")
print(low_confidence_result)

assert low_confidence_result is False


print("\nReliability integration test passed.")