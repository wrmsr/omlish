import abc
import typing as ta

from omlish import lang

from ...tools.execution.catalog import ToolCatalogEntry
from ...tools.types import ToolUse


##


class ToolExecutionRequestDeniedError(Exception):
    pass


class ToolExecutionConfirmation(lang.Abstract):
    @abc.abstractmethod
    def confirm_tool_execution_or_raise(
            self,
            use: ToolUse,
            entry: ToolCatalogEntry,
    ) -> ta.Awaitable[None]:
        raise NotImplementedError


##


class AlwaysDenyToolExecutionConfirmation(ToolExecutionConfirmation):
    async def confirm_tool_execution_or_raise(
            self,
            use: ToolUse,
            entry: ToolCatalogEntry,
    ) -> None:
        raise ToolExecutionRequestDeniedError


class UnsafeAlwaysAllowToolExecutionConfirmation(ToolExecutionConfirmation):
    async def confirm_tool_execution_or_raise(
            self,
            use: ToolUse,
            entry: ToolCatalogEntry,
    ) -> None:
        pass
