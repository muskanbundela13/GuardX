import time

from app.cv.event_definitions import EventTypes
from app.cv.event_schema import SecurityEvent


class EventEngine:
    def process_zone_event(self, zone_event):
        if zone_event is None:
            return None

        if isinstance(zone_event, SecurityEvent):
            return zone_event

        event_type = zone_event["type"]
        track_id = zone_event.get("track_id")
        zone = zone_event.get("zone")
        confidence = zone_event.get("confidence")

        if (
            event_type == "ZONE_ENTRY"
            and zone == "restricted_area"
        ):
            return SecurityEvent(
                event_type=EventTypes.RESTRICTED_ZONE_ENTRY,
                timestamp=time.time(),
                track_id=track_id,
                zone=zone,
                confidence=confidence,
            )

        return None