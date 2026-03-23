import abc
import typing as ta

from omlish import lang


T = ta.TypeVar('T')


##


class StateStorage(lang.Abstract):
    @abc.abstractmethod
    def load_state(self, key: str, ty: type[T] | None) -> ta.Awaitable[T | None]:
        raise NotImplementedError

    @abc.abstractmethod
    def save_state(self, key: str, obj: ta.Any | None, ty: type[T] | None) -> ta.Awaitable[None]:
        raise NotImplementedError
