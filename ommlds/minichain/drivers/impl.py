"""
TODO:
 - lifecycles
 - StreamService
"""
import typing as ta

from omlish.asyncs.asyncio import all as au

from ..chat.messages import Chat
from ..chat.messages import UserChat
from ..chat.transform.chats import MessageTransformChatTransform
from ..chat.transform.messages import CompositeMessageTransform
from ..chat.transform.metadata import CreatedAtAddingMessageTransform
from ..chat.transform.metadata import UuidAddingMessageTransform
from .actions import SendUserMessagesAction
from .ai.types import AiChatGenerator
from .ai.types import GenerateAiChatArgs
from .events.manager import EventsManager
from .phases.manager import PhaseManager
from .phases.types import Phase
from .preparing.types import ChatPreparer
from .state.types import StateManager
from .types import Action
from .types import Driver
from .user.events import UserMessagesEvent


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

        self._lock = au.RLock()

    #

    async def start(self) -> None:
        await self._phases.set_phase(Phase.STARTING)
        await self._phases.set_phase(Phase.STARTED)

    async def stop(self) -> None:
        await self._phases.set_phase(Phase.STOPPING)
        await self._phases.set_phase(Phase.STOPPED)

    #

    async def do_action(self, action: Action) -> None:
        async with self._lock:
            await self._do_action(action)

    async def _do_action(self, action: Action) -> None:
        if isinstance(action, SendUserMessagesAction):
            await self._do_action_send_user_messages(action)

        else:
            raise TypeError(action)

    async def _do_action_send_user_messages(self, action: SendUserMessagesAction) -> None:
        next_user_chat = action.next_user_chat

        next_user_chat = ta.cast(UserChat, MessageTransformChatTransform(CompositeMessageTransform([
            UuidAddingMessageTransform(),
            CreatedAtAddingMessageTransform(),
        ])).transform(next_user_chat))

        await self._events.emit_event(UserMessagesEvent(next_user_chat))

        prev_chat = (await self._chat_state_manager.get_state()).chat

        prepared_chat: Chat = [*prev_chat, *next_user_chat]
        if self._chat_preparer is not None:
            prepared_chat = await self._chat_preparer.prepare_chat(prepared_chat)

        next_ai_chat = await self._ai_chat_generator.generate_ai_chat(GenerateAiChatArgs(prepared_chat))

        await self._chat_state_manager.extend_chat([*next_user_chat, *next_ai_chat])
