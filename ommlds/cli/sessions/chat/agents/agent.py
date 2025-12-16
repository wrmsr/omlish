"""
TODO:
 - lifecycles
 - StreamService
"""
from ..... import minichain as mc
from .ai.types import AiChatGenerator
from .events import AiMessagesChatAgentEvent
from .events import ChatAgentEventSink
from .phases.manager import ChatPhaseManager
from .phases.types import ChatPhase
from .state.types import ChatStateManager


##


class ChatAgent:
    def __init__(
            self,
            *,
            phases: ChatPhaseManager,
            ai_chat_generator: AiChatGenerator,
            chat_state_manager: ChatStateManager,
            event_sink: ChatAgentEventSink,
    ) -> None:
        super().__init__()

        self._phases = phases
        self._ai_chat_generator = ai_chat_generator
        self._chat_state_manager = chat_state_manager
        self._event_sink = event_sink

    async def start(self) -> None:
        await self._phases.set_phase(ChatPhase.STARTING)
        await self._phases.set_phase(ChatPhase.STARTED)

    async def stop(self) -> None:
        await self._phases.set_phase(ChatPhase.STOPPING)
        await self._phases.set_phase(ChatPhase.STOPPED)

    async def send_user_messages(self, next_user_chat: 'mc.UserChat') -> None:
        prev_user_chat = (await self._chat_state_manager.get_state()).chat

        next_ai_chat = await self._ai_chat_generator.get_next_ai_messages([*prev_user_chat, *next_user_chat])

        await self._event_sink(AiMessagesChatAgentEvent(next_ai_chat))

        await self._chat_state_manager.extend_chat([*next_user_chat, *next_ai_chat])
