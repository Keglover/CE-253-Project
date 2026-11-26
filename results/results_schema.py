from dataclasses import dataclass
from ..src.prompting.schema import DefenseVariant

@dataclass
class TrialResult:
    model: str
    task: str
    case_id: str
    defense: DefenseVariant
    retrieved: bool
    payload_reached_prompt: bool
    payload_followed: bool
    tool_attempted: bool
    tool_executed: bool
    unauthorized_action: bool
    visible_compromise: bool
    final_response: str