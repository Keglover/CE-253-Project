from dataclasses import dataclass, field

from model_adapters.base import (
    ChatMessage,
    ModelAdapter,
    ToolCall
)

from .tools import RegisteredTool
from ..prompting.prompt_builder import build_prompt, DefenseVariant
from ..data.normalizer import NormalizedCase
from ..logging.trace_writer import TraceWriter

@dataclass
class HarnessResult:
    case_id: str
    defense: DefenseVariant
    final_response: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    executed_tools: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    messages: list[ChatMessage] = field(default_factory=list)

class AgentHarness:
    def __init__(self, model: ModelAdapter, tools: dict[str, RegisteredTool], *, max_turns: int = 5, trace_logger: TraceWriter=None) -> None:
        self.model = model
        self.tools = tools
        self.max_turns = max_turns
        self.tracer = trace_logger

    def run(self, case: NormalizedCase, *, defense: DefenseVariant = DefenseVariant.BASELINE) -> HarnessResult:
        prompt = build_prompt(case, defense)

        messages = [ChatMessage(role="user", content=prompt)]

        available_tools = [registered.definition for registered in self.tools.values()]

        result = HarnessResult(
            case_id=case.case_id,
            defense=defense,
            messages=messages,
        )

        for turn in range(self.max_turns):
            response = self.model.generate(messages, tools=available_tools)

            if self.tracer is not None:
                self.tracer.write_event(
                    "MODEL RESPONSE:",
                    trial_id=case.case_id,
                    step=turn,
                    content=response.content,
                    tool_calls=response.tool_calls
                )

            if not response.tool_calls:
                result.final_response = response.content
                messages.append(ChatMessage(role="assistant", content=response.content))
                break

            result.tool_calls.extend(response.tool_calls)

            # This assistant message must preserve the requested tool calls.
            messages.append(
                ChatMessage(
                    role="assistant",
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            for call in response.tool_calls:
                tool_result = self._handle_tool_call(call, result)

                messages.append(
                    ChatMessage(
                        role="tool",
                        content=tool_result,
                        name=call.name,
                        tool_call_id=call.call_id,
                    )
                )

        else:
            result.errors.append(f"Maximum turn count reached: {self.max_turns}")

        result.messages = messages
        return result

    def _handle_tool_call(self, call: ToolCall, result: HarnessResult) -> str:
        registered = self.tools.get(call.name)

        if registered is None:
            result.blocked_tools.append(call.name)
            return f"Tool '{call.name}' is not available."

        if not registered.authorized:
            result.blocked_tools.append(call.name)
            return f"Tool '{call.name}' is not authorized."

        try:
            output = registered.function(**call.arguments)
        except Exception as exc:
            result.errors.append(f"Tool '{call.name}' failed: {exc}")
            return f"Tool execution failed: {exc}"

        result.executed_tools.append(call.name)
        return str(output)