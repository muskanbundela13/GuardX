class EventValidator:
    def validate(self, event):
        if event is None:
            return False

        if not event.event_type:
            return False

        if event.timestamp is None:
            return False

        return True