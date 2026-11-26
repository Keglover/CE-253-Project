import json

from pathlib import Path
from annotated_types import dataclass

_PATHS = [
    "code" / "test.jsonl", 
    "email" / "test.jsonl", 
    "table" / "test.jsonl", 
    "qa" / "test.jsonl", 
    "abstract" / "test.jsonl"
]

@dataclass
class ExperimentCase:
    case_id: str
    task: str
    context: str
    question: str
    attack: str
    attack_id: str
    expected_answer: str | None

def json_to_exerpiment_case(json_file : str | Path) -> ExperimentCase:

    def normalize_json(path : Path) -> ExperimentCase:
        with open(path.name, "r", encoding="utf-8") as file:
            data = json.load(file)

            return ExperimentCase(
                case_id=data["case_id"],
                task=data["task"],
                context=data["context"],
                question=data["question"],
                attack=data["attack"],
                attack_id=data["attack_id"],
                expected_answer=data["expected_answer"]
            )

    if isinstance(json_file, Path):
        if json_file.is_file() and json_file.name in _PATHS:
            return normalize_json()

    if isinstance(json_file, str):
        json_path = Path(json_file)
        if json_file in _PATHS and json_path.is_file():
            return normalize_json()