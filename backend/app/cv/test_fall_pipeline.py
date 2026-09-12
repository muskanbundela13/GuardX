from app.cv.fall_detector import FallDetector
from app.cv.event_manager import EventManager
from app.cv.event_reliability import EventReliability


detector = FallDetector()
manager = EventManager()
reliability = EventReliability()

fall_event = detector.detect((100, 200, 300, 280))

print("Detected Fall Event:")
print(fall_event.to_dict() if fall_event else None)

if fall_event:
    event = manager.process_event(fall_event)

    print("\nReliable Event:")
    print(reliability.is_reliable(event))

    print("\nStored Events:")
    print(len(manager.get_events()))

print("\nRepeated Fall Event:")
print(detector.detect((100, 200, 300, 280)))