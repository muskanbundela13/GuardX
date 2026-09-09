import time

from fall_config import (
    FALL_ASPECT_RATIO_THRESHOLD,
    FALL_HEIGHT_THRESHOLD
)
from event_schema import SecurityEvent
from fall_event_debouncer import FallEventDebouncer


class FallDetector:
    def __init__(
        self,
        aspect_ratio_threshold=FALL_ASPECT_RATIO_THRESHOLD,
        height_threshold=FALL_HEIGHT_THRESHOLD
    ):
        self.aspect_ratio_threshold = aspect_ratio_threshold
        self.height_threshold = height_threshold
        self.debouncer = FallEventDebouncer()

    def detect(self, bounding_box):
        x1, y1, x2, y2 = bounding_box

        width = x2 - x1
        height = y2 - y1

        if height <= 0:
            return None

        aspect_ratio = width / height

        if (
            aspect_ratio >= self.aspect_ratio_threshold
            and height <= self.height_threshold
        ):

            if not self.debouncer.should_create_event():
                return None
            return SecurityEvent(
                event_type="FALL_LIKE_EVENT",
                timestamp=time.time(),
                details={
                    "aspect_ratio": aspect_ratio,
                    "width": width,
                    "height": height
                }
            )

        return None