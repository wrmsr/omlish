import abc
import typing as ta

from omlish import lang

from ommlds import minichain as mc


##


class AiChoiceDeltaCallback(lang.Func1[mc.AiChoiceDelta, ta.Awaitable[None]]):
    pass


##


class AiChatGenerator(lang.Abstract):
    @abc.abstractmethod
    def get_next_ai_messages(self, chat: mc.Chat) -> ta.Awaitable[mc.AiChat]:
        raise NotImplementedError
