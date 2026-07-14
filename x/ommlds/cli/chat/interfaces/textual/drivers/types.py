import enum
import typing as ta

from omcore import lang


if ta.TYPE_CHECKING:
    from .interface import ChatDriverInterface  # noqa


##


class ChatDriverInterfaceGetter(lang.AsyncCachedFunc0['ChatDriverInterface']):
    pass


##


InitialTimelineWindowLimit = ta.NewType('InitialTimelineWindowLimit', int)


##


class ChatDriverInterfaceState(enum.StrEnum):
    IDLE = 'idle'
    ACTIVE = 'active'


class ChatDriverInterfaceStateListener(lang.Func2['ChatDriverInterface', ChatDriverInterfaceState, ta.Awaitable[None]]):
    pass
