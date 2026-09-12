from app.cv.crowd_detector import CrowdDetector
from app.cv.event_manager import EventManager


detector = CrowdDetector()
manager = EventManager()

crowd_event = detector.detect([1, 2, 3])

event = manager.process_event(crowd_event)

print("Crowd Event:")
print(event.to_dict())

print("\nStored Events:")
print(len(manager.get_events()))