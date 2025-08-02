import typing as ta

from omlish import check
from ommlds import minichain as mc

from .base import ChatManager


##


class SingleShotChatManager(ChatManager):
    def __init__(self, initial_chat: mc.Chat) -> None:
        super().__init__()

        self._initial_chat = initial_chat
        self._completed_chat: mc.Chat | None = None

    @ta.override
    def get_chat_to_complete(self) -> mc.Chat | None:
        if self._completed_chat is None:
            return self._initial_chat
        else:
            return None

    @ta.override
    def update_chat(self, new_messages: mc.Chat) -> None:
        check.none(self._completed_chat)
        self._completed_chat = [*self._initial_chat, *new_messages]
