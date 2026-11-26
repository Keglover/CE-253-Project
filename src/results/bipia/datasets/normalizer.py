import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExperimentCase:
    case_id: str
    task: str
    context: str
    question: str
    attack: str
    attack_id: str
    expected_answer: str | None = None


def normalize_row(data: dict, *, task: str, line_number: int,) -> ExperimentCase:
    """Convert one raw BIPIA row into the project schema."""

    return ExperimentCase(
        case_id=str(data.get("case_id", f"{task}:test:{line_number}")),
        task=task,
        context=str(data.get("context", data.get("content", ""))),
        question=str(data.get("question", data.get("query", ""))),
        attack=str(data.get("attack", data.get("injection", ""))),
        attack_id=str(data.get("attack_id", data.get("id", line_number))),
        expected_answer=data.get(
            "expected_answer",
            data.get("answer"),
        ),
    )


def jsonl_to_experiment_cases(json_file: str | Path, *, task: str | None = None,) -> list[ExperimentCase]:
    """Load and normalize every record in a BIPIA JSONL file."""

    path = Path(json_file) if isinstance(json_file, str) else json_file

    if not path.is_file():
        raise FileNotFoundError(f"BIPIA dataset file not found: {path}")

    resolved_task = task or path.parent.name
    cases: list[ExperimentCase] = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file):
            if not line.strip():
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number + 1} of {path}"
                ) from exc

            cases.append(
                normalize_row(
                    data,
                    task=resolved_task,
                    line_number=line_number,
                )
            )

    return cases