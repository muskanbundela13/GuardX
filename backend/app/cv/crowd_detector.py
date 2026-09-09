import time
from crowd_event_debouncer import CrowdEventDebouncer
from crowd_config import CROWD_THRESHOLD
from event_schema import SecurityEvent


class CrowdDetector:
    def __init__(self, threshold=CROWD_THRESHOLD):
        self.threshold = threshold
        self.debouncer = CrowdEventDebouncer()

    def detect(self, track_ids):
        crowd_count = len(track_ids)

        if crowd_count >= self.threshold:
            if not self.debouncer.should_create_event():
                return None

            return SecurityEvent(
                event_type="CROWD_ANOMALY",
                timestamp=time.time(),
                details={
                    "crowd_count": crowd_count,
                    "threshold": self.threshold
                }
            )

        return None