from crowd_detector import CrowdDetector
from event_reliability import EventReliability


detector = CrowdDetector()
reliability = EventReliability()


event = detector.detect([1, 2, 3])

print("Crowd Event:")
print(event)

print("\nReliable Crowd Event:")
print(reliability.is_reliable(event))

print("\nDuplicate Crowd Event:")
print(reliability.is_reliable(event))