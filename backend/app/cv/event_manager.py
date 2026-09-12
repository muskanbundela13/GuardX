import time

from app.cv.event_engine import EventEngine
from app.cv.event_schema import SecurityEvent
from app.cv.event_validator import EventValidator


class EventManager:
    def __init__(self):
        self.event_engine = EventEngine()
        self.validator = EventValidator()
        self.events = []

    def process_event(self, raw_event):
        if raw_event is None:
            return None

        if (
            isinstance(raw_event, SecurityEvent)
            or (
                hasattr(raw_event, "event_type")
                and hasattr(raw_event, "timestamp")
                and hasattr(raw_event, "details")
            )
        ):
            security_event = raw_event
        else:
            normalized_event = self.event_engine.process_zone_event(raw_event)

            if normalized_event is None:
                return None

            security_event = normalized_event

        if not self.validator.validate(security_event):
            return None

        self.events.append(security_event)

        return security_event

    def get_events(self):
        """
        Return all stored events.
        """
        return self.events

    def clear_events(self):
        """
        Remove all stored events.
        """
        self.events.clear()