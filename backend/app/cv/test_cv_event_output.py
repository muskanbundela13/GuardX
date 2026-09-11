import time

from event_schema import SecurityEvent
from cv_event_output import CVEventOutput


output_system = CVEventOutput()


# --------------------------------------------------
# Restricted Zone Event
# --------------------------------------------------

zone_event = SecurityEvent(
    event_type="RESTRICTED_ZONE_ENTRY",
    timestamp=time.time(),
    track_id=43,
    zone="restricted_area",
    confidence=None,
    details={
        "reliability_score": 80
    }
)


zone_output = output_system.publish(zone_event)

print("Restricted Zone Output:")
print(zone_output)


assert zone_output["event_type"] == "RESTRICTED_ZONE_ENTRY"
assert zone_output["track_id"] == 43
assert zone_output["zone"] == "restricted_area"
assert zone_output["reliability_score"] == 80


# --------------------------------------------------
# Crowd Event
# --------------------------------------------------

crowd_event = SecurityEvent(
    event_type="CROWD_ANOMALY",
    timestamp=time.time(),
    details={
        "crowd_count": 5,
        "threshold": 3,
        "reliability_score": 80
    }
)


crowd_output = output_system.publish(crowd_event)

print("\nCrowd Output:")
print(crowd_output)


assert crowd_output["event_type"] == "CROWD_ANOMALY"
assert crowd_output["details"]["crowd_count"] == 5
assert crowd_output["reliability_score"] == 80


# --------------------------------------------------
# Aggression Event
# --------------------------------------------------

aggression_event = SecurityEvent(
    event_type="AGGRESSION_LIKE_EVENT",
    timestamp=time.time(),
    details={
        "distance": 32.5,
        "person_1": 0,
        "person_2": 1,
        "reliability_score": 80
    }
)


aggression_output = output_system.publish(
    aggression_event
)

print("\nAggression Output:")
print(aggression_output)


assert (
    aggression_output["event_type"]
    == "AGGRESSION_LIKE_EVENT"
)

assert aggression_output["details"]["distance"] == 32.5
assert aggression_output["reliability_score"] == 80


# --------------------------------------------------
# Fall-like Event
# --------------------------------------------------

fall_event = SecurityEvent(
    event_type="FALL_LIKE_EVENT",
    timestamp=time.time(),
    track_id=101,
    details={
        "aspect_ratio": 1.5,
        "width": 120,
        "height": 80,
        "reliability_score": 85
    }
)


fall_output = output_system.publish(fall_event)

print("\nFall Output:")
print(fall_output)


assert fall_output["event_type"] == "FALL_LIKE_EVENT"
assert fall_output["track_id"] == 101
assert fall_output["reliability_score"] == 85


# --------------------------------------------------
# Invalid Event
# --------------------------------------------------

invalid_output = output_system.publish(None)

print("\nInvalid Output:")
print(invalid_output)

assert invalid_output is None


# --------------------------------------------------
# Stored Outputs
# --------------------------------------------------

outputs = output_system.get_outputs()

print("\nTotal Outputs:")
print(len(outputs))

assert len(outputs) == 4


print("\nCV Event Output contract passed.")