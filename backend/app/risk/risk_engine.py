from typing import Dict, Any


class RiskEngine:

    EVENT_RISK_SCORES = {
        "restricted_zone_entry": 80,
        "aggression_like_event": 70,
        "crowd_anomaly": 60,
        "fall_detected": 90,
    }

    RISK_WEIGHTS = {
        "event_severity": 0.25,
        "time_anomaly": 0.15,
        "zone_sensitivity": 0.15,
        "crowd_anomaly": 0.15,
        "access_violation": 0.10,
        "predicted_baseline_risk": 0.20,
    }

    def get_event_severity(self, event_type: str) -> float:
        return self.EVENT_RISK_SCORES.get(
            event_type.lower(),
            30
        )

    def get_context_value(
        self,
        event: Dict[str, Any],
        field_name: str
    ) -> float:
        value = event.get(field_name, 0)

        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0

        return max(0, min(100, value))

    def calculate_risk(self, event: Dict[str, Any]) -> Dict[str, Any]:
        event_type = event.get(
            "event_type",
            "unknown"
        ).lower()

        event_severity = self.get_event_severity(event_type)

        time_anomaly = self.get_context_value(
            event,
            "time_anomaly"
        )

        zone_sensitivity = self.get_context_value(
            event,
            "zone_sensitivity"
        )

        crowd_anomaly = self.get_context_value(
            event,
            "crowd_anomaly"
        )

        access_violation = self.get_context_value(
            event,
            "access_violation"
        )

        predicted_baseline_risk = self.get_context_value(
            event,
            "predicted_baseline_risk"
        )

        risk_score = (
            event_severity * self.RISK_WEIGHTS["event_severity"]
            + time_anomaly * self.RISK_WEIGHTS["time_anomaly"]
            + zone_sensitivity * self.RISK_WEIGHTS["zone_sensitivity"]
            + crowd_anomaly * self.RISK_WEIGHTS["crowd_anomaly"]
            + access_violation * self.RISK_WEIGHTS["access_violation"]
            + predicted_baseline_risk * self.RISK_WEIGHTS[
                "predicted_baseline_risk"
            ]
        )

        risk_score = round(risk_score, 2)

        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "event_type": event_type,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": {
                "event_severity": event_severity,
                "time_anomaly": time_anomaly,
                "zone_sensitivity": zone_sensitivity,
                "crowd_anomaly": crowd_anomaly,
                "access_violation": access_violation,
                "predicted_baseline_risk": predicted_baseline_risk,
            },
            "risk_weights": self.RISK_WEIGHTS,
            "recommended_action": self.get_action(
                risk_level
            ),
        }

    def get_action(self, risk_level: str) -> str:
        if risk_level == "HIGH":
            return "IMMEDIATE_ALERT"

        if risk_level == "MEDIUM":
            return "MONITOR_AND_NOTIFY"

        return "LOG_EVENT"


risk_engine = RiskEngine()