import abc

from omlish import lang
from ommlds import minichain as mc


##


class ChatCompleter(lang.Abstract):
    @abc.abstractmethod
    def complete_chat(self, chat: mc.Chat) -> mc.Chat:
        raise NotImplementedError
