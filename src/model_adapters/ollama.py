from collections.abc import Sequence

from .base import (
    ChatMessage,
    ModelAdapter,
    ModelResponse,
    ToolDefinition,
)

class OllamaAdapter(ModelAdapter):
    def generate(self, messages: Sequence[ChatMessage], *, tools: Sequence[ToolDefinition] | None = None,) -> ModelResponse:
        # Convert ChatMessage and ToolDefinition objects
        # into Ollama's request format here.
        raise NotImplementedError