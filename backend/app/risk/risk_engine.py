from typing import Dict


class RiskEngine:

    EVENT_RISK_SCORES = {
        "RESTRICTED_ZONE_ENTRY": 80,
        "AGGRESSION_LIKE_EVENT": 70,
        "CROWD_ANOMALY": 60,
        "FALL_DETECTED": 90,
    }

    def calculate_risk(self, event: Dict) -> Dict:
        event_type = event.get("event_type")

        risk_score = self.EVENT_RISK_SCORES.get(
            event_type,
            30
        )

        if risk_score >= 80:
            risk_level = "HIGH"
        elif risk_score >= 50:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "event_type": event_type,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommended_action": self.get_action(
                risk_level
            )
        }

    def get_action(self, risk_level: str) -> str:
        if risk_level == "HIGH":
            return "IMMEDIATE_ALERT"

        if risk_level == "MEDIUM":
            return "MONITOR_AND_NOTIFY"

        return "LOG_EVENT"


risk_engine = RiskEngine()