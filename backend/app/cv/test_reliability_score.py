import time

from event_schema import SecurityEvent
from event_reliability import EventReliability


reliability = EventReliability()

high_confidence_event = SecurityEvent(
    event_type="TEST_EVENT",
    timestamp=time.time(),
    confidence=0.9
)

score = reliability.get_reliability_score(high_confidence_event)

assert high_confidence_event.details["reliability_score"] == 90.0

print("Reliability score test passed.")
print("Score:", score)