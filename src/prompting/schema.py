
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DefenseVariant(StrEnum):
    BASELINE = "baseline"
    REMINDER = "explicit_reminder"
    BOUNDARY = "boundary_awareness"
    COMBINED = "combined"


@dataclass(frozen=True)
class BIPIAExample:
    task: str
    split: str
    context: str
    question: str = ""
    answer: str = ""
    attack: str = ""
    attack_id: str = ""
    insertion_position: str = ""
    source_id: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentCase:
    case_id: str
    example: BIPIAExample
    defense: DefenseVariant = DefenseVariant.BASELINE

    @property
    def task(self) -> str:
        return self.example.task

    @property
    def context(self) -> str:
        return self.example.context

    @property
    def attack(self) -> str:
        return self.example.attack
