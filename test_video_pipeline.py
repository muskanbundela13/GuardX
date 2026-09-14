from backend.app.cv.video_pipeline import VideoPipeline


VIDEO_PATH = r"demo\cctv_test.mp4"

pipeline = VideoPipeline(VIDEO_PATH)

frame_count = 0

while True:
    frame = pipeline.read_frame()

    if frame is None:
        break

    frame_count += 1

    if frame_count <= 5:
        print(
            f"Frame {frame_count}: "
            f"shape={frame.shape}, "
            f"video_time={pipeline.current_time():.2f}s"
        )

pipeline.release()

print("Total frames read:", frame_count)