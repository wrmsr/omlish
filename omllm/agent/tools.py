# flake8: noqa: F401
import typing as ta

from omcore import dataclasses as dc

from .. import llm


type ToolExecutor = ta.Callable[[ToolContext], ta.Awaitable[ToolResult]]


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class ToolContext:
    llm_tool_call: llm.ToolCall


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class ToolResult:
    pass


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class Tool:
    llm_tool: llm.Tool

    @property
    def name(self) -> str:
        return self.llm_tool.name

    executor: ToolExecutor
