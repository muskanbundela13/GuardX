from datetime import datetime
from typing import Dict, Any


class ContextEngine:

    ZONE_SENSITIVITY = {
        "gate a": 90,
        "gate b": 75,
        "parking": 60,
        "lobby": 40,
        "food court": 30,
        "default": 50,
    }

    PREDICTIVE_BASELINE = {
        "gate a": {
            "day": 35,
            "night": 70,
        },
        "gate b": {
            "day": 30,
            "night": 60,
        },
        "parking": {
            "day": 25,
            "night": 65,
        },
        "default": {
            "day": 20,
            "night": 40,
        },
    }

    def get_hour(self, event: Dict[str, Any]) -> int:
        timestamp = event.get("timestamp")

        try:
            timestamp = float(timestamp)
        except (TypeError, ValueError):
            timestamp = 0

        # Video timestamps are treated as seconds from the beginning.
        # Real clock time can be supplied through event["event_datetime"].
        event_datetime = event.get("event_datetime")

        if event_datetime:
            try:
                parsed_datetime = datetime.fromisoformat(
                    event_datetime
                )
                return parsed_datetime.hour
            except ValueError:
                pass

        return int(timestamp // 3600) % 24

    def get_time_anomaly(self, hour: int) -> float:
        if hour >= 22 or hour < 6:
            return 80

        if hour >= 18:
            return 55

        if hour < 9:
            return 45

        return 20

    def get_zone_sensitivity(self, zone: str) -> float:
        zone_name = str(zone or "default").lower()

        return self.ZONE_SENSITIVITY.get(
            zone_name,
            self.ZONE_SENSITIVITY["default"]
        )

    def get_crowd_anomaly(self, event: Dict[str, Any]) -> float:
        value = event.get("crowd_anomaly")

        if value is not None:
            try:
                return max(0, min(100, float(value)))
            except (TypeError, ValueError):
                pass

        crowd_count = event.get("crowd_count")

        if crowd_count is None:
            return 0

        try:
            crowd_count = float(crowd_count)
        except (TypeError, ValueError):
            return 0

        if crowd_count >= 100:
            return 90

        if crowd_count >= 50:
            return 65

        if crowd_count >= 25:
            return 40

        return 15

    def get_access_violation(self, event: Dict[str, Any]) -> float:
        value = event.get("access_violation")

        if value is not None:
            try:
                return max(0, min(100, float(value)))
            except (TypeError, ValueError):
                pass

        if event.get("event_type") == "restricted_zone_entry":
            return 100

        return 0

    def get_predicted_baseline_risk(
        self,
        zone: str,
        hour: int
    ) -> float:
        zone_name = str(zone or "default").lower()

        if zone_name not in self.PREDICTIVE_BASELINE:
            zone_name = "default"

        day_type = "night" if hour >= 22 or hour < 6 else "day"

        return self.PREDICTIVE_BASELINE[zone_name][day_type]

    def build_context(self, event: Dict[str, Any]) -> Dict[str, Any]:
        zone = event.get("zone", "default")
        hour = self.get_hour(event)

        return {
            "hour": hour,
            "time_anomaly": self.get_time_anomaly(hour),
            "zone_sensitivity": self.get_zone_sensitivity(zone),
            "crowd_anomaly": self.get_crowd_anomaly(event),
            "access_violation": self.get_access_violation(event),
            "predicted_baseline_risk": self.get_predicted_baseline_risk(
                zone,
                hour
            ),
        }


context_engine = ContextEngine()