import cv2
from datetime import datetime

from backend.app.cv.video_pipeline import VideoPipeline
from backend.app.database import get_connection


VIDEO_PATH = r"demo\cctv_test.mp4"

pipeline = VideoPipeline(VIDEO_PATH)
connection = get_connection()

previous_gray = None
processed_frames = 0
generated_events = 0

while True:
    frame = pipeline.read_frame()

    if frame is None:
        break

    processed_frames += 1

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if previous_gray is not None:
        difference = cv2.absdiff(previous_gray, gray)
        _, threshold = cv2.threshold(
            difference,
            25,
            255,
            cv2.THRESH_BINARY,
        )

        motion_pixels = cv2.countNonZero(threshold)

        if motion_pixels > 1000:
            video_timestamp = pipeline.current_time()

            cursor = connection.execute(
                """
                INSERT INTO events (
                    event_type,
                    track_id,
                    zone_id,
                    timestamp,
                    confidence,
                    risk_score,
                    risk_level,
                    status,
                    assigned_responder,
                    video_timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "MOTION_DETECTED",
                    None,
                    "ZONE-A",
                    datetime.now().isoformat(),
                    0.90,
                    60.0,
                    "MEDIUM",
                    "OPEN",
                    None,
                    video_timestamp,
                ),
            )

            connection.commit()

            generated_events += 1

            if generated_events <= 5:
                print(
                    "Generated event:",
                    cursor.lastrowid,
                    "video_time:",
                    round(video_timestamp, 2),
                )

    previous_gray = gray

pipeline.release()
connection.close()

print("Processed frames:", processed_frames)
print("Generated events:", generated_events)