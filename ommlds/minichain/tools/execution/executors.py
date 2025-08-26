import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..fns import ToolFn
from ..fns import execute_tool_fn
from .context import ToolContext
from .context import bind_tool_context


##


class ToolExecutor(lang.Abstract):
    @abc.abstractmethod
    def execute_tool(
            self,
            ctx: ToolContext,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> lang.Maywaitable[str]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class ToolFnToolExecutor(ToolExecutor):
    tool_fn: ToolFn

    @lang.maysync
    async def execute_tool(
            self,
            ctx: ToolContext,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> str:
        with bind_tool_context(ctx):
            return await execute_tool_fn(
                self.tool_fn,
                args,
            ).a()


##


@dc.dataclass(frozen=True)
class NameSwitchedToolExecutor(ToolExecutor):
    tool_executors_by_name: ta.Mapping[str, ToolExecutor]

    @lang.maysync
    async def execute_tool(
            self,
            ctx: ToolContext,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> str:
        return await self.tool_executors_by_name[name].execute_tool(ctx, name, args).a()
