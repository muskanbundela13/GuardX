from app.cv.event_schema import SecurityEvent


class CVEventOutput:

    def __init__(self):
        self.output_events = []

    def create_output(self, event):
        if event is None:
            return None

        if not (
            hasattr(event, "event_type")
            and hasattr(event, "timestamp")
            and hasattr(event, "details")
        ):
            return None

        output = {
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "track_id": event.track_id,
            "zone": event.zone,
            "confidence": event.confidence,
            "reliability_score": event.details.get(
                "reliability_score"
            ),
            "details": event.details
        }

        return output

    def publish(self, event):
        output = self.create_output(event)

        if output is None:
            return None

        self.output_events.append(output)

        return output

    def get_outputs(self):
        return self.output_events

    def clear(self):
        self.output_events.clear()