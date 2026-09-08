import cv2
import numpy as np
import json


from video_pipeline import VideoPipeline
from zone_events import ZoneEventDetector
from crowd_detector import CrowdDetector
from event_engine import EventEngine
from tracker import ObjectTracker
from zones import ZONES
from zone_engine import ZoneEngine
zone_engine = ZoneEngine(ZONES)
zone_events = ZoneEventDetector()
zone_engine = ZoneEngine(ZONES)
event_engine = EventEngine()
event_engine = EventEngine()
crowd_detector = CrowdDetector()


VIDEO_PATH = "demo/istockphoto-1995820194-640_adpp_is.mp4"


video = VideoPipeline(VIDEO_PATH)
tracker = ObjectTracker()
zone_engine = ZoneEngine(ZONES)


while True:
    frame = video.read_frame()

    if frame is None:
        break

    result = tracker.track(frame)

    crowd_event = None

    if result.boxes.id is not None:
        track_ids = result.boxes.id.int().cpu().tolist()
        crowd_event = crowd_detector.detect(track_ids)

        if crowd_event is not None:
            print(f"CROWD EVENT: {crowd_event}")

    # Draw YOLO detections
    annotated_frame = result.plot()

    # Draw zones
    for zone_name, polygon in ZONES.items():
        polygon_points = np.array(polygon, dtype=np.int32)

        cv2.polylines(
            annotated_frame,
            [polygon_points],
            True,
            (255, 255, 255),
            2
        )

        x, y = polygon[0]

        cv2.putText(
            annotated_frame,
            zone_name.upper(),
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

    # Check tracked people against zones
    if result.boxes.id is not None:
        boxes = result.boxes.xyxy.cpu().tolist()
        track_ids = result.boxes.id.int().cpu().tolist()

    for box, track_id in zip(boxes, track_ids):
        zone = zone_engine.get_zone(box)

        event = zone_events.update(track_id, zone)

        print(f"Person {track_id} → Zone: {zone}")

        if event is not None:
            print(f"ZONE EVENT: {event}")

            security_event = event_engine.process_zone_event(event)

            if security_event is not None:
                            print(
                "SECURITY EVENT:",
                json.dumps(security_event, indent=2)
            )
    cv2.imshow("GuardX - Zone Engine", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


video.release()
cv2.destroyAllWindows()