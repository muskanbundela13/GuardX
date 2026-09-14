import cv2
from datetime import datetime

from backend.app.cv.video_pipeline import VideoPipeline
from backend.app.database import get_connection


VIDEO_PATH = r"demo\cctv_test.mp4"

COOLDOWN_SECONDS = 3.0
MOTION_THRESHOLD = 1000

pipeline = VideoPipeline(VIDEO_PATH)
connection = get_connection()

previous_gray = None
last_event_time = -COOLDOWN_SECONDS

processed_frames = 0
motion_frames = 0
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

        if motion_pixels > MOTION_THRESHOLD:
            motion_frames += 1

            current_video_time = pipeline.current_time()

            if current_video_time - last_event_time >= COOLDOWN_SECONDS:
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
                        current_video_time,
                    ),
                )

                connection.commit()

                last_event_time = current_video_time
                generated_events += 1

                print(
                    "Generated event:",
                    cursor.lastrowid,
                    "video_time:",
                    round(current_video_time, 2),
                )

    previous_gray = gray

pipeline.release()
connection.close()

print()
print("Processed frames:", processed_frames)
print("Motion-positive frames:", motion_frames)
print("Generated events with cooldown:", generated_events)
print("Cooldown:", COOLDOWN_SECONDS, "seconds")