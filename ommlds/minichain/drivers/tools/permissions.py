import abc
import typing as ta

from omlish import lang

from ...tools.execution.context import tool_context
from ...tools.execution.permissions import DecidedToolPermissionState
from ...tools.execution.permissions import ToolPermissionDecider
from ...tools.permissions.managers import ToolPermissionsManager
from ...tools.permissions.types import ToolPermissionState
from ...tools.permissions.types import ToolPermissionTarget
from .execution import ToolUseExecution


##


class ToolPermissionConfirmation(lang.Abstract):
    @abc.abstractmethod
    def confirm_tool_permission(
            self,
            tue: ToolUseExecution,
            target: ToolPermissionTarget,
    ) -> ta.Awaitable[DecidedToolPermissionState]:
        raise NotImplementedError


#


class AlwaysDenyToolPermissionConfirmation(ToolPermissionConfirmation):
    async def confirm_tool_permission(
            self,
            tue: ToolUseExecution,
            target: ToolPermissionTarget,
    ) -> DecidedToolPermissionState:
        return ToolPermissionState.DENY


class UnsafeAlwaysAllowToolPermissionConfirmation(ToolPermissionConfirmation):
    async def confirm_tool_permission(
            self,
            tue: ToolUseExecution,
            target: ToolPermissionTarget,
    ) -> DecidedToolPermissionState:
        return ToolPermissionState.ALLOW


##


class StandardToolPermissionDecider(ToolPermissionDecider):
    def __init__(
            self,
            *,
            manager: ToolPermissionsManager,
            confirmation: ToolPermissionConfirmation,
    ) -> None:
        super().__init__()

        self._manager = manager
        self._confirmation = confirmation

    async def decide(self, target: ToolPermissionTarget) -> DecidedToolPermissionState:
        m = self._manager.match(target)  # noqa

        tue = tool_context()[ToolUseExecution]

        return await self._confirmation.confirm_tool_permission(tue, target)
