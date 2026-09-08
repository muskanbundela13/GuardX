from event_definitions import EventTypes, create_event


class EventEngine:
    def process_zone_event(self, zone_event):
        if zone_event is None:
            return None

        event_type = zone_event["type"]
        track_id = zone_event["track_id"]
        zone = zone_event["zone"]

        if (
            event_type == "ZONE_ENTRY"
            and zone == "restricted_area"
        ):
            return create_event(
                EventTypes.RESTRICTED_ZONE_ENTRY,
                track_id,
                zone
            )

        return None