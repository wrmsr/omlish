from .chat.ai.types import AiChatGenerator
from .chat.state.types import ChatStateManager
from .chat.user.types import UserChatInput
from .phases.manager import ChatPhaseManager
from .phases.types import ChatPhase


##


class ChatDriver:
    def __init__(
            self,
            *,
            phases: ChatPhaseManager,
            ai_chat_generator: AiChatGenerator,
            user_chat_input: UserChatInput,
            chat_state_manager: ChatStateManager,
    ):
        super().__init__()

        self._phases = phases
        self._ai_chat_generator = ai_chat_generator
        self._user_chat_input = user_chat_input
        self._chat_state_manager = chat_state_manager

    async def run(self) -> None:
        await self._phases.set_phase(ChatPhase.STARTING)
        await self._phases.set_phase(ChatPhase.STARTED)

        while True:
            next_user_chat = await self._user_chat_input.get_next_user_messages()
            if not next_user_chat:
                break

            prev_user_chat = (await self._chat_state_manager.get_state()).chat

            next_ai_chat = await self._ai_chat_generator.get_next_ai_messages([*prev_user_chat, *next_user_chat])

            await self._chat_state_manager.extend_chat([*next_user_chat, *next_ai_chat])

        await self._phases.set_phase(ChatPhase.STOPPING)
        await self._phases.set_phase(ChatPhase.STOPPED)
