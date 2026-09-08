class EventTypes:
    ZONE_ENTRY = "ZONE_ENTRY"
    ZONE_EXIT = "ZONE_EXIT"
    RESTRICTED_ZONE_ENTRY = "RESTRICTED_ZONE_ENTRY"


def create_event(event_type, track_id, zone=None):
    event = {
        "event_type": event_type,
        "track_id": track_id
    }

    if zone is not None:
        event["zone"] = zone

    return event