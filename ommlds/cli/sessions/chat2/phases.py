import dataclasses as dc
import enum
import typing as ta

from omlish import collections as col


##


class ChatSessionPhase(enum.Enum):
    NEW = enum.auto()

    STARTING = enum.auto()
    STARTED = enum.auto()

    STOPPING = enum.auto()
    STOPPED = enum.auto()


##


@dc.dataclass(frozen=True)
class ChatPhaseCallback:
    phase: ChatSessionPhase
    fn: ta.Callable[[], ta.Awaitable[None]]


ChatPhaseCallbacks = ta.NewType('ChatPhaseCallbacks', ta.Sequence[ChatPhaseCallback])


##


class ChatPhaseManager:
    def __init__(self, callbacks: ChatPhaseCallbacks) -> None:
        super().__init__()

        self._callbacks = callbacks
        self._callbacks_by_phase = col.multi_map_by(lambda cb: cb.phase, callbacks)

        self._phase = ChatSessionPhase.NEW

    @property
    def phase(self) -> ChatSessionPhase:
        return self._phase

    async def set_phase(self, phase: ChatSessionPhase) -> None:
        self._phase = phase
        for cb in self._callbacks_by_phase.get(phase, ()):
            await cb.fn()
