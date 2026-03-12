import enum
import typing as ta

from omlish import dataclasses as dc


##


class ChatPhase(enum.Enum):
    NEW = enum.auto()

    STARTING = enum.auto()
    STARTED = enum.auto()

    STOPPING = enum.auto()
    STOPPED = enum.auto()


##


@dc.dataclass(frozen=True)
class ChatPhaseCallback:
    phase: ChatPhase = dc.xfield(validate=lambda v: v != ChatPhase.NEW)
    fn: ta.Callable[[], ta.Awaitable[None]] = dc.xfield()


ChatPhaseCallbacks = ta.NewType('ChatPhaseCallbacks', ta.Sequence[ChatPhaseCallback])
