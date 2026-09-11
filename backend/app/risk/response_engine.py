from typing import Dict


class ResponseEngine:

    def decide(self, risk_result: Dict) -> Dict:
        risk_level = risk_result.get("risk_level")

        if risk_level == "HIGH":
            return {
                "response_type": "ALERT",
                "priority": "URGENT",
                "message": "Immediate security review required."
            }

        if risk_level == "MEDIUM":
            return {
                "response_type": "NOTIFICATION",
                "priority": "NORMAL",
                "message": "Monitor the situation and notify security."
            }

        return {
            "response_type": "LOG",
            "priority": "LOW",
            "message": "Event recorded for future review."
        }


response_engine = ResponseEngine()