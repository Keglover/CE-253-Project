from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal, Sequence

from model_adapters.base import ToolCall

MessageRole = Literal["system", "user", "assistant", "tool"]

@dataclass(frozen=True)
class ChatMessage:
    role: MessageRole
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls : list[ToolCall] = None

    def as_dict(self) -> dict[str, Any]:
        message: dict[str, Any] = {
            "role": self.role,
            "content": self.content,
        }

        if self.name is not None:
            message["name"] = self.name

        if self.tool_call_id is not None:
            message["tool_call_id"] = self.tool_call_id

        return message


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]
    call_id: str | None = None


@dataclass
class ModelResponse:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str | None = None
    finish_reason: str | None = None
    raw_response: Any = None

    @property
    def requested_tool(self) -> bool:
        return bool(self.tool_calls)


class ModelAdapter(ABC):
    def __init__(self, model_name: str, *, temperature: float = 0.0, max_tokens: int | None = None,) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def generate(self, messages: Sequence[ChatMessage], *, tools: Sequence[ToolDefinition] | None = None,) -> ModelResponse:
        """Generate a response from the model."""

    def generate_from_prompt(self, prompt: str, *, system_prompt: str | None = None, tools: Sequence[ToolDefinition] | None = None,) -> ModelResponse:
        """Convenience method for single-prompt smoke tests."""

        messages: list[ChatMessage] = []

        if system_prompt is not None:
            messages.append(ChatMessage(role="system", content=system_prompt))

        messages.append(ChatMessage(role="user", content=prompt))

        return self.generate(messages, tools=tools)