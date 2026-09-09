from fall_event_debouncer import FallEventDebouncer


debouncer = FallEventDebouncer(cooldown_seconds=5)

print("First Event:")
print(debouncer.should_create_event())

print("\nImmediate Second Event:")
print(debouncer.should_create_event())