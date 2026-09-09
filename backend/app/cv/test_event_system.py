import time

from event_schema import SecurityEvent
from event_reliability import EventReliability
from event_logger import EventLogger
from event_statistics import EventStatistics


event = SecurityEvent(
    event_type="RESTRICTED_ZONE_ENTRY",
    timestamp=time.time(),
    track_id=101,
    zone="restricted_area",
    confidence=0.9
)

reliability = EventReliability()
logger = EventLogger("integration_events.jsonl")
statistics = EventStatistics()

print("Reliable Event:")

is_reliable = reliability.is_reliable(event)

print(is_reliable)

if is_reliable:
    logger.log(event)

events = [
    event
]

print("\nLogged Events:")
print(logger.get_events())

print("\nStatistics:")
print(statistics.get_summary(events))

logger.clear()