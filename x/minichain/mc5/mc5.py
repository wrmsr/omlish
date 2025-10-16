"""
input: interactive, oneshot
completion: immediate, stream
rendering: raw, markdown
tools: list
prompt: yes/no
"""
import abc
import typing as ta

from omlish import lang
from ommlds import minichain as mc


##


class UserChatInput(lang.Abstract):
    @abc.abstractmethod
    def get_next_user_messages(self) -> ta.Awaitable[mc.UserChat]:
        raise NotImplementedError


class OneshotUserChatInput(UserChatInput):
    def __init__(
            self,
            initial_chat: mc.UserChat,
    ) -> None:
        super().__init__()

        self._pending_chat: mc.UserChat | None = initial_chat

    async def get_next_user_messages(self) -> mc.UserChat:
        ret = self._pending_chat
        self._pending_chat = None
        return ret or []


class InteractiveUserChatInput(UserChatInput):
    async def get_next_user_messages(self) -> mc.UserChat:
        try:
            prompt = input('> ')  # FIXME: async lol
        except EOFError:
            return []
        return [mc.UserMessage(prompt)]


##


class ToolConfirmation(lang.Abstract):
    pass


class InteractiveToolConfirmation(lang.Abstract):
    pass


##


class ChatStorage(lang.Abstract):
    pass


class InMemoryChatStorage(ChatStorage):
    pass


class JsonFileChatStorage(ChatStorage):
    pass
