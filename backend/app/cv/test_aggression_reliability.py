from aggression_detector import AggressionDetector
from event_reliability import EventReliability


detector = AggressionDetector()
reliability = EventReliability()

close_boxes = [
    (100, 100, 150, 200),
    (130, 110, 180, 210)
]

event = detector.detect(close_boxes)

print("Aggression Event:")
print(event.to_dict() if event else None)

print("\nReliable Event:")
print(reliability.is_reliable(event))