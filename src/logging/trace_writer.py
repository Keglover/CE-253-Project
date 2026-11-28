from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

def _json_default(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Path):
        return str(value)

    raise TypeError(
        f"Object of type {type(value).__name__} is not JSON serializable"
    )

class TraceWriter:
    def __init__(self, output_path: str | Path, *, run_id: str) -> None:
        self.output_path = Path(output_path)
        self.run_id = run_id
        self.sequence = 0

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def write_event(self, event_type: str, *, trial_id: str, step: int | None = None, **payload: Any) -> None:
        self.sequence += 1

        event = {
            "schema_version": "1.0",
            "event_type": event_type,
            "run_id": self.run_id,
            "trial_id": trial_id,
            "sequence": self.sequence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step": step,
            "payload": payload,
        }

        serialized = json.dumps(event, default=_json_default, ensure_ascii=False)

        with self.output_path.open("a", encoding="utf-8") as file:
            file.write(serialized + "\n")