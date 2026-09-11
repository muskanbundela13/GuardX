import numpy as np

from privacy_filter import PrivacyFilter


frame = np.zeros((400, 600, 3), dtype=np.uint8)

privacy_filter = PrivacyFilter()

bounding_boxes = [
    (100, 100, 200, 250),
    (300, 120, 400, 270)
]

original = frame.copy()

result = privacy_filter.apply(frame, bounding_boxes)

assert result.shape == original.shape
assert result.dtype == original.dtype

single_result = privacy_filter.blur_region(
    original.copy(),
    (100, 100, 200, 250)
)

assert single_result.shape == original.shape

print("Privacy filter test passed.")