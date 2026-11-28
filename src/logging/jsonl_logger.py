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

    if isinstance(value, datetime):
        return value.isoformat()

    raise TypeError(
        f"Object of type {type(value).__name__} is not JSON serializable"
    )

class ExperimentLogger:
    
    def __init__(self, output_path: str | Path, *, run_id: str) -> None:
        self.output_path = Path(output_path)
        self.run_id = run_id

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log_trial(self, *, case: Any, result: Any, model_name: str, defense: Any) -> None:
        record = {
            "schema_version": "1.0",
            "event_type": "trial_completed",
            "run_id": self.run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model_name,
            "defense": defense,
            "case": case,
            "result": result,
        }

        serialized = json.dumps(record, default=_json_default, ensure_ascii=False)

        with self.output_path.open("a", encoding="utf-8",) as file:
            file.write(serialized + "\n")