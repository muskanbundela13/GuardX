import json
from pathlib import Path


class EventLogger:
    def __init__(self, log_file="events.jsonl"):
        self.log_file = Path(log_file)

    def log(self, event):
        if event is None:
            return

        with self.log_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event.to_dict()) + "\n")

    def get_events(self):
        if not self.log_file.exists():
            return []

        events = []

        with self.log_file.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line:
                    events.append(json.loads(line))

        return events

    def clear(self):
        if self.log_file.exists():
            self.log_file.unlink()