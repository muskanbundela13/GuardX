from aggression_detector import AggressionDetector


detector = AggressionDetector()

close_boxes = [
    (100, 100, 150, 200),
    (130, 110, 180, 210)
]

print("First Event:")
event1 = detector.detect(close_boxes)
print(event1.to_dict() if event1 else None)

print("\nImmediate Second Event:")
event2 = detector.detect(close_boxes)
print(event2)