from app.cv.reliability_config import (
    CONFIDENCE_THRESHOLD,
    EVENT_COOLDOWN_SECONDS
)

from app.cv.event_validator import EventValidator
from app.cv.event_deduplicator import EventDeduplicator


class EventReliability:

    def __init__(
        self,
        confidence_threshold=CONFIDENCE_THRESHOLD,
        cooldown_seconds=EVENT_COOLDOWN_SECONDS
    ):
        self.confidence_threshold = confidence_threshold
        self.validator = EventValidator()
        self.deduplicator = EventDeduplicator(
            cooldown_seconds=cooldown_seconds
        )

    def _calculate_score(self, event):
        if event.confidence is not None:
            score = event.confidence * 100
        else:
            score = 80

        return round(score, 2)

    def get_reliability_score(self, event):
        if not self.validator.validate(event):
            return 0

        score = self._calculate_score(event)
        event.details["reliability_score"] = score

        return score

    def get_rejection_reason(self, event):
        if event is None:
            return "INVALID_EVENT"

        if not self.validator.validate(event):
            return "VALIDATION_FAILED"

        if (
            event.confidence is not None
            and event.confidence < self.confidence_threshold
        ):
            return "LOW_CONFIDENCE"

        if self.deduplicator.is_duplicate(event):
            return "DUPLICATE_EVENT"

        return None

    def is_reliable(self, event):
        rejection_reason = self.get_rejection_reason(event)

        if rejection_reason is not None:
            return False

        self.get_reliability_score(event)

        return True

    def reset(self):
        self.deduplicator.clear()