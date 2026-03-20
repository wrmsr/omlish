import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..permissions.types import ToolPermissionState
from ..permissions.types import ToolPermissionTarget
from .context import tool_context


##


DecidedToolPermissionState: ta.TypeAlias = ta.Literal[ToolPermissionState.DENY, ToolPermissionState.ALLOW]


class ToolPermissionDecider(lang.Abstract):
    @abc.abstractmethod
    def decide(self, target: ToolPermissionTarget) -> ta.Awaitable[DecidedToolPermissionState]:
        raise NotImplementedError


@ta.final
@dc.dataclass(frozen=True)
class StaticToolPermissionDecider(ToolPermissionDecider):
    state: DecidedToolPermissionState

    async def decide(self, target: ToolPermissionTarget) -> DecidedToolPermissionState:
        return self.state


def tool_permission_decider() -> ToolPermissionDecider:
    return tool_context()[ToolPermissionDecider]  # type: ignore[type-abstract]
