"""
TODO:
 - lifecycles
 - StreamService
"""
from ..chat.messages import Chat
from ..chat.messages import UserChat
from .ai.types import AiChatGenerator
from .events.manager import EventsManager
from .events.types import UserMessagesEvent
from .phases.manager import PhaseManager
from .phases.types import Phase
from .preparing.types import ChatPreparer
from .state.types import StateManager
from .types import Driver


##


class DriverImpl(Driver):
    def __init__(
            self,
            *,
            phases: PhaseManager,
            ai_chat_generator: AiChatGenerator,
            chat_state_manager: StateManager,
            events: EventsManager,
            chat_preparer: ChatPreparer | None = None,
    ) -> None:
        super().__init__()

        self._phases = phases
        self._ai_chat_generator = ai_chat_generator
        self._chat_state_manager = chat_state_manager
        self._events = events
        self._chat_preparer = chat_preparer

    async def start(self) -> None:
        await self._phases.set_phase(Phase.STARTING)
        await self._phases.set_phase(Phase.STARTED)

    async def stop(self) -> None:
        await self._phases.set_phase(Phase.STOPPING)
        await self._phases.set_phase(Phase.STOPPED)

    async def send_user_messages(self, next_user_chat: UserChat) -> None:
        await self._events.emit_event(UserMessagesEvent(next_user_chat))

        prev_chat = (await self._chat_state_manager.get_state()).chat

        prepared_chat: Chat = [*prev_chat, *next_user_chat]
        if self._chat_preparer is not None:
            prepared_chat = await self._chat_preparer.prepare_chat(prepared_chat)

        next_ai_chat = await self._ai_chat_generator.get_next_ai_messages(prepared_chat)

        await self._chat_state_manager.extend_chat([*next_user_chat, *next_ai_chat])
