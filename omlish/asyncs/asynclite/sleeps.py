# @omlish-lite
import abc
import typing as ta

from ...lite.abstract import Abstract


##


class AsyncliteSleeps(Abstract):
    @abc.abstractmethod
    def sleep(self, delay: float) -> ta.Awaitable[None]:
        raise NotImplementedError
