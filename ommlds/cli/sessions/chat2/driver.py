from .phases import ChatPhase
from .phases import ChatPhaseManager


##


class ChatDriver:
    def __init__(
            self,
            *,
            phases: ChatPhaseManager,
    ):
        super().__init__()

        self._phases = phases

    async def run(self) -> None:
        await self._phases.set_phase(ChatPhase.STARTING)
        await self._phases.set_phase(ChatPhase.STARTED)

        await self._phases.set_phase(ChatPhase.STOPPING)
        await self._phases.set_phase(ChatPhase.STOPPED)
