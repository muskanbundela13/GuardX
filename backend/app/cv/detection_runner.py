import cv2
import numpy as np
import json
import urllib.request

from event_reliability import EventReliability
from event_manager import EventManager
from aggression_detector import AggressionDetector
from video_pipeline import VideoPipeline
from zone_events import ZoneEventDetector
from crowd_detector import CrowdDetector
from event_engine import EventEngine
from privacy_filter import PrivacyFilter
from tracker import ObjectTracker
from zones import ZONES
from zone_engine import ZoneEngine
from fall_detector import FallDetector
from cv_event_output import CVEventOutput


zone_engine = ZoneEngine(ZONES)
zone_events = ZoneEventDetector()
event_engine = EventEngine()
crowd_detector = CrowdDetector()
aggression_detector = AggressionDetector()
event_reliability = EventReliability()
event_manager = EventManager()
fall_detector = FallDetector()
privacy_filter = PrivacyFilter()
cv_event_output = CVEventOutput()

VIDEO_PATH = "../../../demo/istockphoto-1995820194-640_adpp_is.mp4"

def send_event_to_backend(event):
    url = "http://127.0.0.1:8000/api/events/ingest"

    request = urllib.request.Request(
        url,
        data=json.dumps(event).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    return result

def publish_backend_event(stored_event, event_label):
    if stored_event is None:
        return None

    backend_event = cv_event_output.publish(stored_event)

    if backend_event is not None:
        print(
            f"CV HANDOFF EVENT ({event_label}):",
            json.dumps(backend_event, indent=2)
        )

        try:
            backend_response = send_event_to_backend(
                backend_event
            )

            print(
                "BACKEND RESPONSE:",
                backend_response["message"]
            )

        except Exception as error:
            print(
                "BACKEND HANDOFF FAILED:",
                error
            )

    return backend_event


video = VideoPipeline(VIDEO_PATH)
tracker = ObjectTracker()
zone_engine = ZoneEngine(ZONES)


while True:
    frame = video.read_frame()

    if frame is None:
        break

    result = tracker.track(frame)

    if result.boxes.id is not None:
        boxes = result.boxes.xyxy.cpu().tolist()
    else:
        boxes = []

    privacy_frame = privacy_filter.apply(
        frame.copy(),
        boxes
    )

    crowd_event = None
    boxes = []
    track_ids = []

    if result.boxes.id is not None:
        track_ids = result.boxes.id.int().cpu().tolist()
        boxes = result.boxes.xyxy.cpu().tolist()

        # -------------------------
        # CROWD EVENT
        # -------------------------

        crowd_event = crowd_detector.detect(track_ids)

        if crowd_event is not None:
            print(f"CROWD EVENT: {crowd_event}")

            if event_reliability.is_reliable(crowd_event):
                stored_event = event_manager.process_event(crowd_event)

                if stored_event is not None:
                    print(
                        "STORED CROWD EVENT:",
                        json.dumps(
                            stored_event.to_dict(),
                            indent=2
                        )
                    )

                    publish_backend_event(
                        stored_event,
                        "CROWD"
                    )

        # -------------------------
        # AGGRESSION EVENT
        # -------------------------

        aggression_event = aggression_detector.detect(boxes)

        if aggression_event is not None:
            print(f"AGGRESSION EVENT: {aggression_event}")

            if event_reliability.is_reliable(aggression_event):
                stored_event = event_manager.process_event(
                    aggression_event
                )

                if stored_event is not None:
                    print(
                        "STORED AGGRESSION EVENT:",
                        json.dumps(
                            stored_event.to_dict(),
                            indent=2
                        )
                    )

                    publish_backend_event(
                        stored_event,
                        "AGGRESSION"
                    )

        # -------------------------
        # FALL EVENT
        # -------------------------

        for box, track_id in zip(boxes, track_ids):

            fall_event = fall_detector.detect(box)

            if fall_event is not None:
                fall_event.track_id = track_id

                print(f"FALL EVENT: {fall_event}")

                if event_reliability.is_reliable(fall_event):
                    stored_event = event_manager.process_event(
                        fall_event
                    )

                    if stored_event is not None:
                        print(
                            "STORED FALL EVENT:",
                            json.dumps(
                                stored_event.to_dict(),
                                indent=2
                            )
                        )

                        publish_backend_event(
                            stored_event,
                            "FALL"
                        )

    # -------------------------
    # ANNOTATED FRAME
    # -------------------------

    annotated_frame = result.plot(
        img=privacy_frame
    )

    for zone_name, polygon in ZONES.items():

        polygon_points = np.array(
            polygon,
            dtype=np.int32
        )

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

    # -------------------------
    # ZONE EVENTS
    # -------------------------

    if result.boxes.id is not None:

        boxes = result.boxes.xyxy.cpu().tolist()

        track_ids = (
            result.boxes.id
            .int()
            .cpu()
            .tolist()
        )

    for box, track_id in zip(boxes, track_ids):

        zone = zone_engine.get_zone(box)

        event = zone_events.update(
            track_id,
            zone
        )

        print(
            f"Person {track_id} → Zone: {zone}"
        )

        if event is not None:
            print(
                f"ZONE EVENT: {event}"
            )

        security_event = (
            event_engine.process_zone_event(event)
        )

        if security_event is not None:

            if event_reliability.is_reliable(
                security_event
            ):

                stored_event = (
                    event_manager.process_event(
                        security_event
                    )
                )

                if stored_event is not None:

                    print(
                        "STORED SECURITY EVENT:",
                        json.dumps(
                            stored_event.to_dict(),
                            indent=2
                        )
                    )

                    publish_backend_event(
                        stored_event,
                        "ZONE"
                    )

    # -------------------------
    # DISPLAY
    # -------------------------

    cv2.imshow(
        "GuardX - Zone Engine",
        annotated_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


video.release()
cv2.destroyAllWindows()


# -------------------------
# FINAL HANDOFF SUMMARY
# -------------------------

print("\n==============================")
print("GUARDX CV HANDOFF SUMMARY")
print("==============================")

print(
    "Total backend-ready events:",
    len(cv_event_output.get_outputs())
)

for event in cv_event_output.get_outputs():
    print(
        json.dumps(
            event,
            indent=2
        )
    )