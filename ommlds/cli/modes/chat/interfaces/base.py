import abc
import typing as ta

from omlish import lang


##


class ChatInterface(lang.Abstract):
    @abc.abstractmethod
    def run(self) -> ta.Awaitable[None]:
        raise NotImplementedError
