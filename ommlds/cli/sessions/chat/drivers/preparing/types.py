import abc
import typing as ta

from omlish import lang

from ...... import minichain as mc


##


class ChatPreparer(lang.Abstract):
    @abc.abstractmethod
    def prepare_chat(self, chat: 'mc.Chat') -> ta.Awaitable['mc.Chat']:
        raise NotImplementedError
