import abc
import typing as ta

from omcore import lang


##


class ChatInterface(lang.Abstract):
    @abc.abstractmethod
    def run(self) -> ta.Awaitable[None]:
        raise NotImplementedError
