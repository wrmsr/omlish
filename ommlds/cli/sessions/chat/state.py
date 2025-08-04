import abc
import dataclasses as dc
import datetime

from omlish import check
from omlish import lang

from .... import minichain as mc
from ...state import StateStorage


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: mc.Chat = ()


##


class ChatStateManager(lang.Abstract):
    @abc.abstractmethod
    def get_state(self) -> ChatState:
        raise NotImplementedError

    @abc.abstractmethod
    def clear_state(self) -> ChatState:
        raise NotImplementedError

    @abc.abstractmethod
    def extend_chat(self, chat_additions: mc.Chat) -> ChatState:
        raise NotImplementedError


##


class InMemoryChatStateManager(ChatStateManager):
    def __init__(self, initial_state: ChatState | None = None) -> None:
        super().__init__()

        if initial_state is None:
            initial_state = ChatState()
        self._state = initial_state

    def get_state(self) -> ChatState:
        return self._state

    def clear_state(self) -> ChatState:
        self._state = ChatState()
        return self._state

    def extend_chat(self, chat_additions: mc.Chat) -> ChatState:
        self._state = dc.replace(
            self._state,
            chat=[*self._state.chat, *chat_additions],
            updated_at=lang.utcnow(),
        )
        return self._state


##


class StateStorageChatStateManager(ChatStateManager):
    def __init__(
            self,
            *,
            storage: StateStorage,
            key: str = 'chat',
    ) -> None:
        super().__init__()

        self._storage = storage
        self._key = check.non_empty_str(key)

        self._state: ChatState | None = None

    def get_state(self) -> ChatState:
        if self._state is not None:
            return self._state
        state: ChatState | None = self._storage.load_state(self._key, ChatState)
        if state is None:
            state = ChatState()
        self._state = state
        return state

    def clear_state(self) -> ChatState:
        state = ChatState()
        self._storage.save_state(self._key, state, ChatState)
        self._state = state
        return state

    def extend_chat(self, chat_additions: mc.Chat) -> ChatState:
        state = self.get_state()
        state = dc.replace(
            state,
            chat=[*state.chat, *chat_additions],
            updated_at=lang.utcnow(),
        )
        self._storage.save_state(self._key, state, ChatState)
        return state
