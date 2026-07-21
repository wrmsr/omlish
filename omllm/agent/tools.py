# flake8: noqa: F401
import typing as ta

from omcore import dataclasses as dc

from .. import llm


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class ToolContext:
    pass


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class ToolResult:
    pass


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class Tool:
    llm: llm.Tool

    fn: ta.Callable[[ToolContext], ToolResult]
