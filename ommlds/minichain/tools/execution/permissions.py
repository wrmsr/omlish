import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..permissions.types import ToolPermissionState
from ..permissions.types import ToolPermissionTarget
from .context import tool_context
from .errors import PermissionDeniedToolExecutionError


##


DecidedToolPermissionState: ta.TypeAlias = ta.Literal[ToolPermissionState.DENY, ToolPermissionState.ALLOW]


class ToolPermissionDecider(lang.Abstract):
    @abc.abstractmethod
    def decide(self, target: ToolPermissionTarget) -> ta.Awaitable[DecidedToolPermissionState]:
        raise NotImplementedError

    async def is_allowed(self, target: ToolPermissionTarget) -> bool:
        return (await self.decide(target)) is ToolPermissionState.ALLOW

    async def check_allowed(self, target: ToolPermissionTarget) -> None:
        if not await self.is_allowed(target):
            raise PermissionDeniedToolExecutionError(target)


#


@ta.final
@dc.dataclass(frozen=True)
class StaticToolPermissionDecider(ToolPermissionDecider):
    state: DecidedToolPermissionState

    async def decide(self, target: ToolPermissionTarget) -> DecidedToolPermissionState:
        return self.state


##


def tool_permission_decider() -> ToolPermissionDecider:
    return tool_context()[ToolPermissionDecider]  # type: ignore[type-abstract]
