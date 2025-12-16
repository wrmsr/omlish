from omlish import check
from omlish import collections as col

from .types import ChatPhase
from .types import ChatPhaseCallbacks


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
