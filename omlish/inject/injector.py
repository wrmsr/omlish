import abc
import typing as ta

from .. import lang
from .elements import Elements
from .inspect import KwargsTarget
from .keys import Key


_impl = lang.proxy_import('.impl.injector', __package__)


T = ta.TypeVar('T')


class Injector(lang.Abstract):
    @abc.abstractmethod
    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, key: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def provide_kwargs(self, kt: KwargsTarget) -> ta.Mapping[str, ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(self, obj: ta.Any) -> ta.Any:
        raise NotImplementedError

    def __getitem__(
            self,
            target: Key[T] | type[T],
    ) -> T:
        return self.provide(target)


def create_injector(es: Elements) -> Injector:
    return _impl.create_injector(es)
