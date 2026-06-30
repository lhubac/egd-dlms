from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class CosemObject:
    class_id: int
    logical_name: str
    full_obis: str
    attribute: int
    value: Any

@dataclass(slots=True)
class MeterState:
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    values: dict[str, Any] = field(default_factory=dict)

    def to_payload(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            **diagnostics,
            **self.values,
        }
