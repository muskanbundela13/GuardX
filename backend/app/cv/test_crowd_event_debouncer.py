from crowd_event_debouncer import CrowdEventDebouncer


debouncer = CrowdEventDebouncer(cooldown_seconds=5)

print("First Event:")
print(debouncer.should_create_event())

print("\nImmediate Second Event:")
print(debouncer.should_create_event())