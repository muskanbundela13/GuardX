from event_validator import EventValidator
from event_deduplicator import EventDeduplicator


class EventReliability:
    def __init__(self, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        self.validator = EventValidator()
        self.deduplicator = EventDeduplicator()

    def is_reliable(self, event):
        if not self.validator.validate(event):
            return False

        if (
            event.confidence is not None
            and event.confidence < self.confidence_threshold
        ):
            return False

        if self.deduplicator.is_duplicate(event):
            return False

        return True

    def reset(self):
        self.deduplicator.clear()