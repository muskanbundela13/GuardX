import cv2


class VideoPipeline:
    def __init__(self, video_source):
        self.video_source = video_source
        self.capture = cv2.VideoCapture(video_source)

        if not self.capture.isOpened():
            raise ValueError(f"Could not open video source: {video_source}")

    def read_frame(self):
        success, frame = self.capture.read()

        if not success:
            return None

        return frame

    def release(self):
        self.capture.release()