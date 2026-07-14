"""
TODO:
 - args is Mapping[str, Content] too
"""
import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ...content.content import Content
from ..fns import ToolFn
from ..fns import invoke_tool_fn


##


class ToolInvoker(lang.Abstract):
    @abc.abstractmethod
    def invoke_tool(
            self,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> ta.Awaitable[Content]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class ToolFnToolInvoker(ToolInvoker):
    tool_fn: ToolFn

    async def invoke_tool(
            self,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> Content:
        return await invoke_tool_fn(
            self.tool_fn,
            args,
        )


##


@dc.dataclass(frozen=True)
class NameSwitchedToolInvoker(ToolInvoker):
    invokers_by_name: ta.Mapping[str, ToolInvoker]

    async def invoke_tool(
            self,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> Content:
        return await self.invokers_by_name[name].invoke_tool(name, args)
