from crowd_detector import CrowdDetector


detector = CrowdDetector()

print("Below Threshold:")
print(detector.detect([1, 2]))

print("\nAt Threshold:")
print(detector.detect([1, 2, 3]))

print("\nAbove Threshold:")
print(detector.detect([1, 2, 3, 4]))