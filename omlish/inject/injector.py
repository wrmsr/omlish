import abc
import typing as ta

from .. import check
from .. import lang
from .elements import CollectedElements
from .elements import Elemental
from .elements import as_elements
from .elements import collect_elements
from .inspect import KwargsTarget
from .keys import Key


if ta.TYPE_CHECKING:
    from .impl import injector as _injector
else:
    _injector = lang.proxy_import('.impl.injector', __package__)


T = ta.TypeVar('T')


##


class AsyncInjector(lang.Abstract):
    @abc.abstractmethod
    def try_provide(self, key: ta.Any) -> ta.Awaitable[lang.Maybe[ta.Any]]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, key: ta.Any) -> ta.Awaitable[ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide_kwargs(self, kt: KwargsTarget) -> ta.Awaitable[ta.Mapping[str, ta.Any]]:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(self, obj: ta.Any) -> ta.Awaitable[ta.Any]:
        raise NotImplementedError

    def __getitem__(
            self,
            target: Key[T] | type[T],
    ) -> ta.Awaitable[T]:
        return self.provide(target)


##


@ta.final
class _InjectorCreator(ta.Generic[T]):
    def __init__(self, fac: ta.Callable[[CollectedElements], T]) -> None:
        self._fac = fac

    @ta.overload
    def __call__(self, es: CollectedElements, /) -> T: ...

    @ta.overload
    def __call__(self, *es: Elemental) -> T: ...

    def __call__(self, arg0, *argv):
        ce: CollectedElements
        if isinstance(arg0, CollectedElements):
            check.arg(not argv)
            ce = arg0
        else:
            ce = collect_elements(as_elements(arg0, *argv))
        return self._fac(ce)


##


create_async_injector = _InjectorCreator[ta.Awaitable[AsyncInjector]](lambda ce: _injector.create_async_injector(ce))
