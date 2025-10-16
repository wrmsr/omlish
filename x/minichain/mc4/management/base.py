import abc

from omlish import lang
from ommlds import minichain as mc


##


class ChatManager(lang.Abstract):
    @abc.abstractmethod
    def get_chat_to_complete(self) -> mc.Chat | None:
        raise NotImplementedError

    @abc.abstractmethod
    def update_chat(self, new_messages: mc.Chat) -> None:
        raise NotImplementedError
