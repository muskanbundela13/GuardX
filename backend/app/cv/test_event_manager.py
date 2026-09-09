from event_manager import EventManager


manager = EventManager()

raw_event = {
    "type": "ZONE_ENTRY",
    "track_id": 43,
    "zone": "restricted_area"
}

event = manager.process_event(raw_event)

print("Generated Event:")
print(event.to_dict())

print("\nNumber of Stored Events:")
print(len(manager.get_events()))

print("\nClearing Events...")
manager.clear_events()

print("Number of Stored Events After Clear:")
print(len(manager.get_events()))