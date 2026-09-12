import cv2


class PrivacyFilter:

    def apply(self, frame, bounding_boxes=None):
        """
        Apply privacy blurring to the supplied bounding boxes.
        """

        if bounding_boxes is None:
            return frame

        result = frame.copy()

        for bounding_box in bounding_boxes:
            result = self.blur_region(result, bounding_box)

        return result

    def blur_region(self, frame, bounding_box):
        """
        Blur one rectangular region.

        bounding_box format:
        (x1, y1, x2, y2)
        """

        x1, y1, x2, y2 = bounding_box

        height, width = frame.shape[:2]

        x1 = max(0, min(x1, width))
        x2 = max(0, min(x2, width))
        y1 = max(0, min(y1, height))
        y2 = max(0, min(y2, height))

        if x1 >= x2 or y1 >= y2:
            return frame

        region = frame[y1:y2, x1:x2]

        if region.size == 0:
            return frame

        blurred_region = cv2.GaussianBlur(
            region,
            (51, 51),
            0,
        )

        frame[y1:y2, x1:x2] = blurred_region

        return frame