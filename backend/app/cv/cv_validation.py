from collections import Counter


class CVValidation:

    REQUIRED_FIELDS = {
        "event_type",
        "timestamp",
        "track_id",
        "zone",
        "confidence",
        "reliability_score",
        "details"
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self.total_frames = 0
        self.frames_with_detections = 0
        self.total_events = 0
        self.valid_events = 0
        self.invalid_events = 0

        self.event_types = Counter()
        self.validation_errors = []

    def record_frame(self, detections=None):
        self.total_frames += 1

        if detections:
            self.frames_with_detections += 1

    def validate_event(self, event):
        self.total_events += 1

        if not isinstance(event, dict):
            self.invalid_events += 1
            self.validation_errors.append(
                "Event is not a dictionary"
            )
            return False

        missing_fields = self.REQUIRED_FIELDS - set(event.keys())

        if missing_fields:
            self.invalid_events += 1
            self.validation_errors.append(
                f"Missing fields: {sorted(missing_fields)}"
            )
            return False

        if not event["event_type"]:
            self.invalid_events += 1
            self.validation_errors.append(
                "event_type is empty"
            )
            return False

        if event["timestamp"] is None:
            self.invalid_events += 1
            self.validation_errors.append(
                "timestamp is missing"
            )
            return False

        if not isinstance(event["details"], dict):
            self.invalid_events += 1
            self.validation_errors.append(
                "details must be a dictionary"
            )
            return False

        self.valid_events += 1
        self.event_types[event["event_type"]] += 1

        return True

    def get_detection_rate(self):
        if self.total_frames == 0:
            return 0.0

        return round(
            (self.frames_with_detections / self.total_frames) * 100,
            2
        )

    def get_event_validity_rate(self):
        if self.total_events == 0:
            return 0.0

        return round(
            (self.valid_events / self.total_events) * 100,
            2
        )

    def get_summary(self):
        return {
            "total_frames": self.total_frames,
            "frames_with_detections": self.frames_with_detections,
            "detection_rate": self.get_detection_rate(),
            "total_events": self.total_events,
            "valid_events": self.valid_events,
            "invalid_events": self.invalid_events,
            "event_validity_rate": self.get_event_validity_rate(),
            "event_types": dict(self.event_types),
            "validation_errors": self.validation_errors
        }