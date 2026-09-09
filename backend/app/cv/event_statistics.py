from collections import Counter


class EventStatistics:
    def get_summary(self, events):
        if not events:
            return {
                "total_events": 0,
                "event_types": {},
                "zones": {}
            }

        event_types = Counter(
            event.event_type for event in events
        )

        zones = Counter(
            event.zone
            for event in events
            if event.zone is not None
        )

        return {
            "total_events": len(events),
            "event_types": dict(event_types),
            "zones": dict(zones)
        }