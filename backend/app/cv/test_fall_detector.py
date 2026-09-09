from fall_detector import FallDetector


detector = FallDetector()

print("Normal Standing:")
print(detector.detect((100, 100, 150, 250)))

print("\nFall-like Position:")
event = detector.detect((100, 200, 300, 280))
print(event.to_dict() if event else None)

print("\nInvalid Box:")
print(detector.detect((100, 100, 150, 100)))