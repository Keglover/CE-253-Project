import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class NormalizedCase:
    case_id: str
    task: str
    context: str
    question: str
    attack: str
    attack_id: str
    expected_answer: str | None = None
    insertion_position: str | None = None

def normalize_row(data: dict, *, line_number: int,) -> NormalizedCase:
    ideal = data.get("ideal")

    return NormalizedCase(
        case_id=(
            f"{data['task_name']}:test:"
            f"{data['attack_name']}:{line_number}"
        ),
        task=data["task_name"],
        context=data["context"],
        question=data["question"],
        attack=data["attack_str"],
        attack_id=data["attack_name"],
        expected_answer=ideal,
        insertion_position=data.get("position"),
    )

def jsonl_to_experiment_cases(json_path: str | Path) -> list[NormalizedCase]:
    path = Path(json_path) if isinstance(json_path, str) else json_path
    cases = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file):
            if not line.strip():
                continue

            data = json.loads(line)
            cases.append(
                normalize_row(
                    data,
                    line_number=line_number,
                )
            )

    return cases