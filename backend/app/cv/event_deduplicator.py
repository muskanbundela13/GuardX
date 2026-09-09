import time


class EventDeduplicator:
    def __init__(self, cooldown_seconds=5):
        self.cooldown_seconds = cooldown_seconds
        self.last_events = {}

    def is_duplicate(self, event):
        if event is None:
            return False

        key = (
            event.event_type,
            event.track_id,
            event.zone
        )

        current_time = time.time()
        last_event = self.last_events.get(key)

        if last_event is not None:
            if current_time - last_event.timestamp < self.cooldown_seconds:
                return True

        self.last_events[key] = event
        return False

    def clear(self):
        self.last_events.clear()