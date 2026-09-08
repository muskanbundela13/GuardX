from crowd_config import CROWD_THRESHOLD

class CrowdDetector:
    def __init__(self, threshold=CROWD_THRESHOLD):
        self.threshold = threshold

    def detect(self, track_ids):
        crowd_count = len(track_ids)

        if crowd_count >= self.threshold:
            return {
                "event_type": "CROWD_ANOMALY",
                "crowd_count": crowd_count,
                "threshold": self.threshold
            }

        return None