import time


class FallEventDebouncer:
    def __init__(self, cooldown_seconds=5):
        self.cooldown_seconds = cooldown_seconds
        self.last_event_time = None

    def should_create_event(self):
        current_time = time.time()

        if self.last_event_time is None:
            self.last_event_time = current_time
            return True

        if current_time - self.last_event_time >= self.cooldown_seconds:
            self.last_event_time = current_time
            return True

        return False

    def reset(self):
        self.last_event_time = None