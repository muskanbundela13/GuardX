import time

from event_evaluator import EventEvaluator
from event_reliability import EventReliability
from event_schema import SecurityEvent


def create_event(
    event_type,
    track_id,
    confidence,
    zone="restricted_area"
):
    return SecurityEvent(
        event_type=event_type,
        timestamp=time.time(),
        track_id=track_id,
        zone=zone,
        confidence=confidence
    )


reliability = EventReliability(
    cooldown_seconds=5
)

evaluator = EventEvaluator(reliability)


events = [
    create_event(
        event_type="RESTRICTED_ZONE_ENTRY",
        track_id=1,
        confidence=0.95
    ),
    create_event(
        event_type="CROWD_ANOMALY",
        track_id=2,
        confidence=0.90
    ),
    create_event(
        event_type="FALL_LIKE_EVENT",
        track_id=3,
        confidence=0.80
    ),
    create_event(
        event_type="AGGRESSION_LIKE_EVENT",
        track_id=4,
        confidence=0.40
    ),
    create_event(
        event_type="RESTRICTED_ZONE_ENTRY",
        track_id=5,
        confidence=0.85
    )
]


for event in events:
    result = evaluator.evaluate_event(event)

    print(
        event.event_type,
        "→",
        "ACCEPTED" if result["accepted"] else "REJECTED"
    )


summary = evaluator.get_summary()


print("\nEvaluation Summary:")
print("Total Events:", summary["total_events"])
print("Accepted Events:", summary["accepted_events"])
print("Rejected Events:", summary["rejected_events"])
print("Acceptance Rate:", summary["acceptance_rate"], "%")
print(
    "Average Reliability:",
    summary["average_reliability"]
)

print("\nEvent Types:")
for event_type, count in summary["event_types"].items():
    print(event_type, ":", count)

print("\nAccepted Event Types:")
for event_type, count in summary["accepted_event_types"].items():
    print(event_type, ":", count)

print("\nRejection Reasons:")
for reason, count in summary["rejection_reasons"].items():
    print(reason, ":", count)


assert summary["total_events"] == 5
assert summary["accepted_events"] == 4
assert summary["rejected_events"] == 1
assert summary["acceptance_rate"] == 80.0
assert summary["average_reliability"] == 87.5
assert summary["rejection_reasons"]["LOW_CONFIDENCE"] == 1

print("\nEvent evaluation passed.")