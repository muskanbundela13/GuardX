import time

from aggression_config import AGGRESSION_DISTANCE_THRESHOLD
from aggression_event_debouncer import AggressionEventDebouncer
from event_schema import SecurityEvent


class AggressionDetector:
    def __init__(self, distance_threshold=AGGRESSION_DISTANCE_THRESHOLD):
        self.distance_threshold = distance_threshold
        self.debouncer = AggressionEventDebouncer()

    def detect(self, bounding_boxes):
        if len(bounding_boxes) < 2:
            return None

        for i in range(len(bounding_boxes)):
            for j in range(i + 1, len(bounding_boxes)):

                x1, y1, x2, y2 = bounding_boxes[i]
                a1, b1, a2, b2 = bounding_boxes[j]

                center1 = ((x1 + x2) / 2, (y1 + y2) / 2)
                center2 = ((a1 + a2) / 2, (b1 + b2) / 2)

                distance = (
                    (center1[0] - center2[0]) ** 2
                    + (center1[1] - center2[1]) ** 2
                ) ** 0.5

                if distance <= self.distance_threshold:

                    if not self.debouncer.should_create_event():
                        return None

                    return SecurityEvent(
                        event_type="AGGRESSION_LIKE_EVENT",
                        timestamp=time.time(),
                        details={
                            "distance": distance,
                            "person_1": i,
                            "person_2": j
                        }
                    )

        return None