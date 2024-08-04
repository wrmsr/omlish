import abc
import typing as ta

from .. import lang
from .elements import Elemental
from .elements import as_elements
from .inspect import KwargsTarget
from .keys import Key


if ta.TYPE_CHECKING:
    from .impl import injector as _injector
else:
    _injector = lang.proxy_import('.impl.injector', __package__)


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


def create_injector(*args: Elemental) -> Injector:
    return _injector.create_injector(as_elements(*args))
