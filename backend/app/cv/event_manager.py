import time

from event_engine import EventEngine
from event_schema import SecurityEvent


class EventManager:
    def __init__(self):
        self.event_engine = EventEngine()
        self.events = []

    def process_event(self, raw_event):
        """
        Process and store a standardized SecurityEvent.
        """

        if raw_event is None:
            return None

        if isinstance(raw_event, SecurityEvent):
            self.events.append(raw_event)
            return raw_event

        normalized_event = self.event_engine.process_zone_event(raw_event)

        if normalized_event is None:
            return None

        if isinstance(normalized_event, SecurityEvent):
            security_event = normalized_event
        else:
            security_event = SecurityEvent(
                event_type=normalized_event["event_type"],
                timestamp=time.time(),
                track_id=normalized_event.get("track_id"),
                zone=normalized_event.get("zone"),
                confidence=normalized_event.get("confidence"),
                details=normalized_event.get("details", {})
            )

        self.events.append(security_event)

        return security_event

    def get_events(self):
        """
        Return all events currently stored by the manager.
        """
        return self.events

    def clear_events(self):
        """
        Remove all stored events.
        """
        self.events.clear()