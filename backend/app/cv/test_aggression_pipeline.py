from aggression_detector import AggressionDetector
from event_reliability import EventReliability
from event_manager import EventManager


detector = AggressionDetector()
reliability = EventReliability()
manager = EventManager()

close_boxes = [
    (100, 100, 150, 200),
    (130, 110, 180, 210)
]

event = detector.detect(close_boxes)

print("Detected Aggression Event:")
print(event.to_dict() if event else None)

if reliability.is_reliable(event):
    stored_event = manager.process_event(event)

    print("\nStored Event:")
    print(stored_event.to_dict() if stored_event else None)

print("\nStored Events:")
print(len(manager.get_events()))