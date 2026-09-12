class EventValidator:
    def validate(self, event):
        if event is None:
            return False

        if not getattr(event, "event_type", None):
            return False

        if getattr(event, "timestamp", None) is None:
            return False

        event_type = event.event_type

        if event_type == "RESTRICTED_ZONE_ENTRY":
            if event.track_id is None:
                return False

            if event.zone is None:
                return False

            if event.confidence is None:
                return False

        if event.confidence is not None:
            if not 0 <= event.confidence <= 1:
                return False

        return True