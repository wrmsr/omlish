import abc
import typing as ta

from omlish import lang

from ...chat.messages import Chat


##


class ChatPreparer(lang.Abstract):
    @abc.abstractmethod
    def prepare_chat(self, chat: Chat) -> ta.Awaitable[Chat]:
        raise NotImplementedError
