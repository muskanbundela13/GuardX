import cv2
from backend.app.cv.video_pipeline import VideoPipeline


VIDEO_PATH = r"demo\cctv_test.mp4"

pipeline = VideoPipeline(VIDEO_PATH)

frame = pipeline.read_frame()

if frame is None:
    raise RuntimeError("No frame was returned from the video")

gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

print("Original frame shape:", frame.shape)
print("Grayscale frame shape:", gray_frame.shape)
print("Frame data type:", frame.dtype)
print("Grayscale data type:", gray_frame.dtype)

pipeline.release()