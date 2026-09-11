from typing import Dict, List


class EventStore:

    def __init__(self):
        self.events: List[Dict] = []

    def add_event(self, event: Dict) -> Dict:
        self.events.append(event)
        return event

    def get_events(self) -> List[Dict]:
        return self.events

    def get_event_count(self) -> int:
        return len(self.events)

    def clear_events(self) -> None:
        self.events.clear()


event_store = EventStore()