import time

from event_schema import SecurityEvent
from event_deduplicator import EventDeduplicator


deduplicator = EventDeduplicator(cooldown_seconds=5)

event = SecurityEvent(
    event_type="AGGRESSION_LIKE_EVENT",
    timestamp=time.time()
)

assert deduplicator.is_duplicate(event) is False
assert deduplicator.is_duplicate(event) is True

time.sleep(5.1)

new_event = SecurityEvent(
    event_type="AGGRESSION_LIKE_EVENT",
    timestamp=time.time()
)

assert deduplicator.is_duplicate(new_event) is False

deduplicator.clear()

print("Event deduplication test passed.")