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


##


class InMemoryStateStorage(StateStorage):
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict[str, ta.Any] = {}

    async def load_state(self, key: str, ty: type[T] | None) -> T | None:
        return self._dct.get(key)

    async def save_state(self, key: str, obj: ta.Any | None, ty: type[T] | None) -> None:
        if obj is None:
            self._dct.pop(key, None)
        else:
            self._dct[key] = obj
