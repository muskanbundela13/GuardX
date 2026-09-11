from datetime import datetime
from typing import Dict, Any, List


class IncidentManager:
    def __init__(self):
        self.incidents: Dict[str, Dict[str, Any]] = {}
        self.next_incident_id = 1

    def create_incident(self, event: Dict[str, Any]) -> Dict[str, Any]:
        incident_id = f"INC-{self.next_incident_id:04d}"
        self.next_incident_id += 1

        incident = {
            "incident_id": incident_id,
            "status": "OPEN",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "event_count": 1,
            "events": [event],
            "latest_event": event,
        }

        self.incidents[incident_id] = incident
        return incident

    def add_event(self, incident_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
        incident = self.incidents.get(incident_id)

        if incident is None:
            return {
                "status": "error",
                "message": "Incident not found",
            }

        incident["events"].append(event)
        incident["event_count"] = len(incident["events"])
        incident["latest_event"] = event
        incident["updated_at"] = datetime.utcnow().isoformat()

        return incident

    def update_status(self, incident_id: str, status: str) -> Dict[str, Any]:
        incident = self.incidents.get(incident_id)

        if incident is None:
            return {
                "status": "error",
                "message": "Incident not found",
            }

        allowed_statuses = ["OPEN", "ACKNOWLEDGED", "RESOLVED"]

        if status not in allowed_statuses:
            return {
                "status": "error",
                "message": f"Invalid status. Use one of: {allowed_statuses}",
            }

        incident["status"] = status
        incident["updated_at"] = datetime.utcnow().isoformat()

        return incident

    def get_incident(self, incident_id: str):
        return self.incidents.get(incident_id)

    def get_all_incidents(self) -> List[Dict[str, Any]]:
        return list(self.incidents.values())


incident_manager = IncidentManager()