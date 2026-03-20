import abc
import typing as ta

from omlish import lang

from ...chat.messages import ToolUseResultMessage
from .execution import ToolUseExecution
from .execution import ToolUseExecutor


##


class ToolExecutionRequestDeniedError(Exception):
    pass


class ToolExecutionConfirmation(lang.Abstract):
    @abc.abstractmethod
    def confirm_tool_execution_or_raise(self, tue: ToolUseExecution) -> ta.Awaitable[None]:
        raise NotImplementedError


#


class AlwaysDenyToolExecutionConfirmation(ToolExecutionConfirmation):
    async def confirm_tool_execution_or_raise(self, tue: ToolUseExecution) -> None:
        raise ToolExecutionRequestDeniedError


class UnsafeAlwaysAllowToolExecutionConfirmation(ToolExecutionConfirmation):
    async def confirm_tool_execution_or_raise(self, tue: ToolUseExecution) -> None:
        pass


##


class ConfirmingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
            confirmation: ToolExecutionConfirmation,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._confirmation = confirmation

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResultMessage:
        await self._confirmation.confirm_tool_execution_or_raise(tue)

        return await self._wrapped.execute_tool_use(tue)
