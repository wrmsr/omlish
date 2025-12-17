import abc
import typing as ta

from omlish import lang

from ...... import minichain as mc


##


class ToolExecutionRequestDeniedError(Exception):
    pass


class ToolExecutionConfirmation(lang.Abstract):
    @abc.abstractmethod
    def confirm_tool_execution_or_raise(
            self,
            use: 'mc.ToolUse',
            entry: 'mc.ToolCatalogEntry',
    ) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class AlwaysDenyToolExecutionConfirmation(ToolExecutionConfirmation):
    async def confirm_tool_execution_or_raise(
            self,
            use: 'mc.ToolUse',
            entry: 'mc.ToolCatalogEntry',
    ) -> None:
        raise ToolExecutionRequestDeniedError


class UnsafeAlwaysAllowToolExecutionConfirmation(ToolExecutionConfirmation):
    async def confirm_tool_execution_or_raise(
            self,
            use: 'mc.ToolUse',
            entry: 'mc.ToolCatalogEntry',
    ) -> None:
        pass
