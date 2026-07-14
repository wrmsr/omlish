import abc
import typing as ta

from omcore import lang


##


ProfileName = ta.NewType('ProfileName', str)


##


class Entrypoint(lang.Abstract):
    @abc.abstractmethod
    def run(self) -> ta.Awaitable[None]:
        raise NotImplementedError
