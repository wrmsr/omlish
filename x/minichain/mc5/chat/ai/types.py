import abc
import typing as ta

from omlish import check
from omlish import lang

from ommlds import minichain as mc


##


class AiChatGenerator(lang.Abstract):
    @abc.abstractmethod
    def get_next_ai_messages(self, chat: mc.Chat) -> ta.Awaitable[mc.AiChat]:
        raise NotImplementedError
