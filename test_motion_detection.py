import cv2
from backend.app.cv.video_pipeline import VideoPipeline


VIDEO_PATH = r"demo\cctv_test.mp4"

pipeline = VideoPipeline(VIDEO_PATH)

previous_gray = None
motion_frames = 0
processed_frames = 0

while True:
    frame = pipeline.read_frame()

    if frame is None:
        break

    processed_frames += 1

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if previous_gray is not None:
        difference = cv2.absdiff(previous_gray, gray)
        _, threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)

        motion_pixels = cv2.countNonZero(threshold)

        if motion_pixels > 1000:
            motion_frames += 1

    previous_gray = gray

pipeline.release()

print("Processed frames:", processed_frames)
print("Frames with motion:", motion_frames)