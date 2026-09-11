from event_reliability import EventReliability
from event_schema import SecurityEvent


def create_event(
    track_id,
    confidence,
    event_type="RESTRICTED_ZONE_ENTRY"
):
    return SecurityEvent(
        event_type=event_type,
        timestamp=float(track_id),
        track_id=track_id,
        zone="restricted_area",
        confidence=confidence
    )


reliability = EventReliability()


events = [
    create_event(1, 0.95),
    create_event(2, 0.90),
    create_event(3, 0.80),
    create_event(4, 0.70),
]


accepted_events = []

for event in events:

    if reliability.is_reliable(event):
        accepted_events.append(event)


print("Total Events:", len(events))
print("Accepted Events:", len(accepted_events))

print("\nReliability Scores:")

for event in accepted_events:
    print(
        event.track_id,
        "→",
        event.details["reliability_score"]
    )


assert len(accepted_events) == 4

assert accepted_events[0].details["reliability_score"] == 95.0
assert accepted_events[1].details["reliability_score"] == 90.0
assert accepted_events[2].details["reliability_score"] == 80.0
assert accepted_events[3].details["reliability_score"] == 70.0


print("\nReliability evaluation passed.")