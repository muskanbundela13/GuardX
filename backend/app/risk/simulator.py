from typing import Dict, Any


class ResponseSimulator:

    STRATEGIES = {
        "do_nothing": {
            "risk_reduction": 0,
            "response_cost": 0,
            "response_time": 0,
            "action": "LOG_EVENT",
        },
        "send_guard": {
            "risk_reduction": 25,
            "response_cost": 20,
            "response_time": 5,
            "action": "SEND_GUARD",
        },
        "restrict_entrance": {
            "risk_reduction": 35,
            "response_cost": 30,
            "response_time": 3,
            "action": "RESTRICT_ENTRANCE",
        },
        "send_guard_and_restrict": {
            "risk_reduction": 60,
            "response_cost": 45,
            "response_time": 5,
            "action": "SEND_GUARD_AND_RESTRICT",
        },
    }

    def simulate(
        self,
        current_risk: float,
        strategy: str
    ) -> Dict[str, Any]:

        if strategy not in self.STRATEGIES:
            return {
                "status": "error",
                "message": "Unknown response strategy",
                "available_strategies": list(
                    self.STRATEGIES.keys()
                ),
            }

        strategy_data = self.STRATEGIES[strategy]

        risk_reduction = strategy_data["risk_reduction"]

        remaining_risk = max(
            0,
            round(current_risk - risk_reduction, 2)
        )

        return {
            "strategy": strategy,
            "action": strategy_data["action"],
            "initial_risk": current_risk,
            "risk_reduction": risk_reduction,
            "remaining_risk": remaining_risk,
            "response_cost": strategy_data["response_cost"],
            "response_time_minutes": strategy_data[
                "response_time"
            ],
        }

    def compare_strategies(
        self,
        current_risk: float
    ) -> Dict[str, Any]:

        results = []

        for strategy in self.STRATEGIES:
            results.append(
                self.simulate(
                    current_risk,
                    strategy
                )
            )

        recommended = min(
            results,
            key=lambda result: (
                result["remaining_risk"],
                result["response_cost"],
                result["response_time_minutes"],
            )
        )

        return {
            "status": "success",
            "initial_risk": current_risk,
            "strategies": results,
            "recommended_strategy": recommended["strategy"],
            "recommended_action": recommended["action"],
        }


response_simulator = ResponseSimulator()