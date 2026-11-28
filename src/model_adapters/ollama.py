from __future__ import annotations

import json
from collections.abc import Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import (
    ChatMessage,
    ModelAdapter,
    ModelResponse,
    ToolCall,
    ToolDefinition,
)

class OllamaAdapter(ModelAdapter):

    def __init__(self, model_name: str, *, host: str = "localhost", port: int = 11434, temperature: float = 0.0, max_tokens: int | None = None, timeout: float = 120.0,) -> None:
        
        super().__init__(
            model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout

    def generate(self, messages: Sequence[ChatMessage], *, tools: Sequence[ToolDefinition] | None = None,) -> ModelResponse:
        
        payload: dict = {
            "model": self.model_name,
            "messages": [
                message.as_dict()
                for message in messages
            ],
            "stream": False,
        }

        payload["tools"] = [tool.as_dict() for tool in tools] if tools else None

        options: dict = {
            "temperature": self.temperature,
        }

        if self.max_tokens is not None:
            options["num_predict"] = self.max_tokens

        payload["options"] = options

        response_data = self._post_json(
            endpoint="/api/chat",
            payload=payload,
        )

        message_data = response_data.get("message", {})
        content = message_data.get("content", "")

        tool_calls = []

        for raw_tool_call in message_data.get("tool_calls", []):
            function_data = raw_tool_call.get("function", {})

            arguments = function_data.get("arguments", {})

            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError as exc:
                    raise ValueError("Ollama returned invalid JSON tool arguments") from exc

            if not isinstance(arguments, dict):
                raise TypeError("Ollama tool arguments must be a JSON object")

            tool_calls.append(ToolCall(name=function_data["name"],arguments=arguments,call_id=raw_tool_call.get("id")))

        return ModelResponse(
            content=content,
            tool_calls=tool_calls,
            model=response_data.get("model", self.model_name),
            finish_reason=response_data.get("done_reason"),
            raw_response=response_data,
        )

    def _post_json(self, *, endpoint: str, payload: dict) -> dict:
        
        request = Request(
            url=f"{self.base_url}{endpoint}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_body = response.read().decode("utf-8")

        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama returned HTTP {exc.code}: {error_body}") from exc

        except URLError as exc:
            raise ConnectionError(f"Could not connect to Ollama at {self.base_url}. Make sure Ollama is running.") from exc

        try:
            parsed = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise ValueError("Ollama returned a response that was not valid JSON") from exc

        if not isinstance(parsed, dict):
            raise TypeError("Ollama response must be a JSON object")

        return parsed