from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class SecurityEvent:
    event_type: str
    timestamp: float
    track_id: Optional[int] = None
    zone: Optional[str] = None
    confidence: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "track_id": self.track_id,
            "zone": self.zone,
            "confidence": self.confidence,
            "details": self.details
        }