"""
TODO:
 - lifecycles
 - StreamService
"""
from ..chat.messages import Chat
from ..chat.messages import UserChat
from .ai.types import AiChatGenerator
from .events.manager import ChatEventsManager
from .events.types import UserMessagesChatEvent
from .phases.manager import ChatPhaseManager
from .phases.types import ChatPhase
from .preparing.types import ChatPreparer
from .state.types import ChatStateManager
from .types import ChatDriver


##


class ChatDriverImpl(ChatDriver):
    def __init__(
            self,
            *,
            phases: ChatPhaseManager,
            ai_chat_generator: AiChatGenerator,
            chat_state_manager: ChatStateManager,
            events: ChatEventsManager,
            chat_preparer: ChatPreparer | None = None,
    ) -> None:
        super().__init__()

        self._phases = phases
        self._ai_chat_generator = ai_chat_generator
        self._chat_state_manager = chat_state_manager
        self._events = events
        self._chat_preparer = chat_preparer

    async def start(self) -> None:
        await self._phases.set_phase(ChatPhase.STARTING)
        await self._phases.set_phase(ChatPhase.STARTED)

    async def stop(self) -> None:
        await self._phases.set_phase(ChatPhase.STOPPING)
        await self._phases.set_phase(ChatPhase.STOPPED)

    async def send_user_messages(self, next_user_chat: UserChat) -> None:
        await self._events.emit_event(UserMessagesChatEvent(next_user_chat))

        prev_chat = (await self._chat_state_manager.get_state()).chat

        prepared_chat: Chat = [*prev_chat, *next_user_chat]
        if self._chat_preparer is not None:
            prepared_chat = await self._chat_preparer.prepare_chat(prepared_chat)

        next_ai_chat = await self._ai_chat_generator.get_next_ai_messages(prepared_chat)

        await self._chat_state_manager.extend_chat([*next_user_chat, *next_ai_chat])
