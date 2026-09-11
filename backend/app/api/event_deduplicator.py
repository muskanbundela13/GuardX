import time
from typing import Dict, Tuple


class EventDeduplicator:

    def __init__(self):
        self.cooldowns = {
            "RESTRICTED_ZONE_ENTRY": 10,
            "AGGRESSION_LIKE_EVENT": 15,
            "CROWD_ANOMALY": 20,
            "FALL_DETECTED": 10,
            "FALL_LIKE_EVENT": 10,
        }

        self.last_events: Dict[Tuple, float] = {}

    def should_accept(self, event: Dict) -> bool:
        event_type = event.get("event_type", "UNKNOWN")
        track_id = event.get("track_id")
        zone = event.get("zone")

        details = event.get("details", {})

        person_1 = details.get("person_1")
        person_2 = details.get("person_2")

        if event_type == "AGGRESSION_LIKE_EVENT":
            event_key = (
                event_type,
                person_1,
                person_2
            )
        elif event_type in {
            "CROWD_ANOMALY",
            "FALL_DETECTED",
            "FALL_LIKE_EVENT"
        }:
            event_key = (
                event_type,
                zone
            )
        else:
            event_key = (
                event_type,
                track_id,
                zone
            )

        current_time = time.time()

        previous_time = self.last_events.get(event_key)

        cooldown = self.cooldowns.get(
            event_type,
            10
        )

        if previous_time is not None:
            elapsed = current_time - previous_time

            if elapsed < cooldown:
                return False

        self.last_events[event_key] = current_time

        return True


event_deduplicator = EventDeduplicator()