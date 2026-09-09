import time

from event_schema import SecurityEvent
from event_statistics import EventStatistics


events = [
    SecurityEvent(
        event_type="RESTRICTED_ZONE_ENTRY",
        timestamp=time.time(),
        track_id=1,
        zone="restricted_area",
        confidence=0.9
    ),
    SecurityEvent(
        event_type="RESTRICTED_ZONE_ENTRY",
        timestamp=time.time(),
        track_id=2,
        zone="restricted_area",
        confidence=0.8
    ),
    SecurityEvent(
        event_type="ZONE_EXIT",
        timestamp=time.time(),
        track_id=1,
        zone="restricted_area",
        confidence=0.9
    )
]

statistics = EventStatistics()

print("Event Statistics:")
print(statistics.get_summary(events))