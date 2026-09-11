from cv_validation import CVValidation


validator = CVValidation()


# Simulate processed frames.
validator.record_frame(
    detections=[
        {"track_id": 1, "class": "person"}
    ]
)

validator.record_frame(
    detections=[
        {"track_id": 2, "class": "person"}
    ]
)

validator.record_frame(
    detections=[]
)


valid_events = [
    {
        "event_type": "RESTRICTED_ZONE_ENTRY",
        "timestamp": 1234567890.0,
        "track_id": 1,
        "zone": "restricted_area",
        "confidence": 0.95,
        "reliability_score": 95.0,
        "details": {}
    },
    {
        "event_type": "CROWD_ANOMALY",
        "timestamp": 1234567891.0,
        "track_id": None,
        "zone": "restricted_area",
        "confidence": 0.90,
        "reliability_score": 90.0,
        "details": {
            "crowd_count": 8
        }
    },
    {
        "event_type": "FALL_LIKE_EVENT",
        "timestamp": 1234567892.0,
        "track_id": 3,
        "zone": None,
        "confidence": 0.85,
        "reliability_score": 85.0,
        "details": {
            "aspect_ratio": 1.5
        }
    }
]


invalid_event = {
    "event_type": "INVALID_EVENT",
    "timestamp": 1234567893.0
}


for event in valid_events:
    result = validator.validate_event(event)
    assert result is True


assert validator.validate_event(invalid_event) is False


summary = validator.get_summary()


print("CV Validation Summary:")
print("Total Frames:", summary["total_frames"])
print(
    "Frames With Detections:",
    summary["frames_with_detections"]
)
print("Detection Rate:", summary["detection_rate"], "%")
print("Total Events:", summary["total_events"])
print("Valid Events:", summary["valid_events"])
print("Invalid Events:", summary["invalid_events"])
print(
    "Event Validity Rate:",
    summary["event_validity_rate"],
    "%"
)

print("\nEvent Types:")
for event_type, count in summary["event_types"].items():
    print(event_type, ":", count)

print("\nValidation Errors:")
for error in summary["validation_errors"]:
    print("-", error)


assert summary["total_frames"] == 3
assert summary["frames_with_detections"] == 2
assert summary["detection_rate"] == 66.67
assert summary["total_events"] == 4
assert summary["valid_events"] == 3
assert summary["invalid_events"] == 1
assert summary["event_validity_rate"] == 75.0

print("\nCV validation passed.")