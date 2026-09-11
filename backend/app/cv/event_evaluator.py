from collections import Counter


class EventEvaluator:

    def __init__(self, reliability):
        self.reliability = reliability
        self.reset()

    def reset(self):
        self.total_events = 0
        self.accepted_events = 0
        self.rejected_events = 0

        self.rejection_reasons = Counter()
        self.event_types = Counter()
        self.accepted_event_types = Counter()

        self.reliability_scores = []

    def evaluate_event(self, event):
        self.total_events += 1

        if event is not None:
            self.event_types[event.event_type] += 1

        rejection_reason = self.reliability.get_rejection_reason(event)

        if rejection_reason is not None:
            self.rejected_events += 1
            self.rejection_reasons[rejection_reason] += 1

            return {
                "accepted": False,
                "reason": rejection_reason,
                "event": event
            }

        self.accepted_events += 1
        self.accepted_event_types[event.event_type] += 1

        reliability_score = self.reliability.get_reliability_score(event)
        self.reliability_scores.append(reliability_score)

        return {
            "accepted": True,
            "reason": None,
            "event": event,
            "reliability_score": reliability_score
        }

    def get_acceptance_rate(self):
        if self.total_events == 0:
            return 0.0

        return round(
            (self.accepted_events / self.total_events) * 100,
            2
        )

    def get_average_reliability(self):
        if not self.reliability_scores:
            return 0.0

        return round(
            sum(self.reliability_scores)
            / len(self.reliability_scores),
            2
        )

    def get_summary(self):
        return {
            "total_events": self.total_events,
            "accepted_events": self.accepted_events,
            "rejected_events": self.rejected_events,
            "acceptance_rate": self.get_acceptance_rate(),
            "average_reliability": self.get_average_reliability(),
            "event_types": dict(self.event_types),
            "accepted_event_types": dict(self.accepted_event_types),
            "rejection_reasons": dict(self.rejection_reasons)
        }