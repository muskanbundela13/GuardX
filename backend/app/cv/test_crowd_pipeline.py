from app.cv.crowd_detector import CrowdDetector
from app.cv.event_manager import EventManager
from app.cv.event_reliability import EventReliability


detector = CrowdDetector()
manager = EventManager()
reliability = EventReliability()

crowd_event = detector.detect([1, 2, 3])

print("Detected Crowd Event:")
print(crowd_event.to_dict() if crowd_event else None)

if crowd_event:
    event = manager.process_event(crowd_event)

    print("\nReliable Event:")
    print(reliability.is_reliable(event))

    print("\nStored Events:")
    print(len(manager.get_events()))

print("\nRepeated Crowd Event:")
print(detector.detect([1, 2, 3]))