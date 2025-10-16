from .chat.ai.types import AiChatGenerator
from .chat.user.types import UserChatInput
from .phases import ChatPhase
from .phases import ChatPhaseManager


##


class ChatDriver:
    def __init__(
            self,
            *,
            phases: ChatPhaseManager,
            ai_chat_generator: AiChatGenerator,
            user_chat_input: UserChatInput,
    ):
        super().__init__()

        self._phases = phases
        self._ai_chat_generator = ai_chat_generator
        self._user_chat_input = user_chat_input

    async def run(self) -> None:
        await self._phases.set_phase(ChatPhase.STARTING)
        await self._phases.set_phase(ChatPhase.STARTED)

        await self._phases.set_phase(ChatPhase.STOPPING)
        await self._phases.set_phase(ChatPhase.STOPPED)
