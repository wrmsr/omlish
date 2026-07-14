from omlish import check
from omlish import collections as col

from .types import Phase
from .types import PhaseCallbacks


##


class PhaseManager:
    def __init__(self, callbacks: PhaseCallbacks) -> None:
        super().__init__()

        self._callbacks = callbacks
        self._callbacks_by_phase = col.multi_map_by(lambda cb: cb.phase, callbacks)

        check.state(not self._callbacks_by_phase.get(Phase.NEW))

        self._phase = Phase.NEW

    @property
    def phase(self) -> Phase:
        return self._phase

    async def set_phase(self, phase: Phase) -> None:
        self._phase = phase
        for cb in self._callbacks_by_phase.get(phase, ()):
            await cb.fn()
