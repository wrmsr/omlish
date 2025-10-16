import typing as ta

from omlish import lang
from ommlds import minichain as mc

from .base import ChatManager


if ta.TYPE_CHECKING:
    from omdev import ptk

else:
    ptk = lang.proxy_import('omdev.ptk')


##


class InteractiveChatManager(ChatManager):
    def __init__(self, initial_chat: mc.Chat | None = None) -> None:
        super().__init__()

        self._chat = list(initial_chat or [])
        self._last_sent_chat_len = -1

    @ta.override
    def get_chat_to_complete(self) -> mc.Chat | None:
        if len(self._chat) == self._last_sent_chat_len:
            raise RuntimeError

        if not self._chat or not isinstance(self._chat[-1], mc.UserMessage):
            prompt = ptk.prompt('> ')
            if not prompt:
                return None

            self._chat.append(mc.UserMessage(prompt))

        self._last_sent_chat_len = len(self._chat)
        return self._chat

    @ta.override
    def update_chat(self, new_messages: mc.Chat) -> None:
        self._chat.extend(new_messages)
