import enum
import typing as ta

from omlish import check
from omlish import collections as col
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


##


class ChatPhaseManager:
    def __init__(self, callbacks: ChatPhaseCallbacks) -> None:
        super().__init__()

        self._callbacks = callbacks
        self._callbacks_by_phase = col.multi_map_by(lambda cb: cb.phase, callbacks)

        check.state(not self._callbacks_by_phase.get(ChatPhase.NEW))

        self._phase = ChatPhase.NEW

    @property
    def phase(self) -> ChatPhase:
        return self._phase

    async def set_phase(self, phase: ChatPhase) -> None:
        self._phase = phase
        for cb in self._callbacks_by_phase.get(phase, ()):
            await cb.fn()
