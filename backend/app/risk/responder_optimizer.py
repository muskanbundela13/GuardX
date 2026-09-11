from typing import Dict, Any, List


class ResponderOptimizer:

    RESPONDERS = [
        {
            "responder_id": "G-001",
            "name": "Guard Alpha",
            "available": True,
            "distance": 120,
            "workload": 20,
            "capabilities": [
                "restricted_zone",
                "crowd_control",
                "medical",
            ],
        },
        {
            "responder_id": "G-002",
            "name": "Guard Bravo",
            "available": True,
            "distance": 250,
            "workload": 10,
            "capabilities": [
                "restricted_zone",
                "crowd_control",
            ],
        },
        {
            "responder_id": "G-003",
            "name": "Guard Charlie",
            "available": False,
            "distance": 80,
            "workload": 30,
            "capabilities": [
                "medical",
                "restricted_zone",
            ],
        },
        {
            "responder_id": "G-004",
            "name": "Guard Delta",
            "available": True,
            "distance": 400,
            "workload": 5,
            "capabilities": [
                "crowd_control",
                "restricted_zone",
            ],
        },
    ]

    def get_required_capability(
        self,
        event_type: str
    ) -> str:
        if event_type == "fall_detected":
            return "medical"

        if event_type == "crowd_anomaly":
            return "crowd_control"

        return "restricted_zone"

    def calculate_score(
        self,
        responder: Dict[str, Any]
    ) -> float:
        distance_score = responder["distance"] / 10
        workload_score = responder["workload"]

        return round(
            distance_score + workload_score,
            2
        )

    def recommend(
        self,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:

        event_type = event.get(
            "event_type",
            "unknown"
        ).lower()

        required_capability = self.get_required_capability(
            event_type
        )

        eligible_responders: List[Dict[str, Any]] = []

        for responder in self.RESPONDERS:
            if not responder["available"]:
                continue

            if required_capability not in responder["capabilities"]:
                continue

            responder_copy = responder.copy()
            responder_copy["selection_score"] = self.calculate_score(
                responder
            )

            eligible_responders.append(responder_copy)

        if not eligible_responders:
            return {
                "status": "unavailable",
                "message": "No suitable responder is currently available",
                "required_capability": required_capability,
                "recommended_responder": None,
                "eligible_responders": [],
            }

        eligible_responders.sort(
            key=lambda responder: responder["selection_score"]
        )

        recommended_responder = eligible_responders[0]

        return {
            "status": "success",
            "required_capability": required_capability,
            "recommended_responder": recommended_responder,
            "eligible_responders": eligible_responders,
        }

    def get_all_responders(self) -> List[Dict[str, Any]]:
        return self.RESPONDERS


responder_optimizer = ResponderOptimizer()