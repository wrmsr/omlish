import abc
import typing as ta

from .. import lang
from .mappers import Mapper
from .snaps import Snap


##


class Store(lang.Abstract):
    class Context(lang.Abstract):
        @property
        @abc.abstractmethod
        def store(self) -> Store:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def finish(self) -> ta.Awaitable[None]:
            raise NotImplementedError

        @abc.abstractmethod
        def abort(self) -> ta.Awaitable[None]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def fetch(self, m: Mapper, k: ta.Any) -> ta.Awaitable[Snap | None]:
            raise NotImplementedError

        @abc.abstractmethod
        def lookup(self, m: Mapper, where: ta.Mapping[str, ta.Any]) -> ta.Awaitable[ta.Sequence[Snap]]:
            raise NotImplementedError

        #

        @abc.abstractmethod
        def auto_key_insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> ta.Awaitable[ta.Mapping[ta.Any, ta.Any]]:
            raise NotImplementedError

        @abc.abstractmethod
        def insert(self, m: Mapper, snaps: ta.Sequence[Snap]) -> ta.Awaitable[None]:
            raise NotImplementedError

        @abc.abstractmethod
        def update(self, m: Mapper, diffs: ta.Sequence[tuple[ta.Any, Snap]]) -> ta.Awaitable[None]:
            raise NotImplementedError

        @abc.abstractmethod
        def delete(self, m: Mapper, keys: ta.Sequence[ta.Any]) -> ta.Awaitable[None]:
            raise NotImplementedError

    @abc.abstractmethod
    def create_context(
            self,
            *,
            transaction: bool | ta.Literal['default'] = 'default',
    ) -> ta.AsyncContextManager[Context]:
        raise NotImplementedError
