from event_validator import EventValidator
from event_schema import SecurityEvent


validator = EventValidator()


valid_event = SecurityEvent(
    event_type="RESTRICTED_ZONE_ENTRY",
    timestamp=1000,
    track_id=43,
    zone="restricted_area"
)

invalid_event = SecurityEvent(
    event_type="",
    timestamp=1000,
    track_id=43,
    zone="restricted_area"
)


print("Valid Event:")
print(validator.validate(valid_event))

print("\nInvalid Event:")
print(validator.validate(invalid_event))

print("\nNone Event:")
print(validator.validate(None))