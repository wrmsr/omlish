import abc
import typing as ta

from .. import lang
from .injector import _InjectorCreator
from .inspect import KwargsTarget
from .keys import Key


if ta.TYPE_CHECKING:
    from .impl import sync as _sync
else:
    _sync = lang.proxy_import('.impl.sync', __package__)


T = ta.TypeVar('T')


##


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


##


create_injector = _InjectorCreator[Injector](lambda ce: _sync.create_injector(ce))
