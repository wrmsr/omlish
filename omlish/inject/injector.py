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
T_contra = ta.TypeVar('T_contra', contravariant=True)
R = ta.TypeVar('R')
R_co = ta.TypeVar('R_co', covariant=True)


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


class _InjectorCreatorFactory(ta.Protocol[T_contra, R_co]):
    def __call__(self, ce: CollectedElements, p: T_contra | None = None, /) -> R_co: ...


@ta.final
class _InjectorCreator(ta.Generic[T, R]):
    def __init__(self, fac: _InjectorCreatorFactory[T, R]) -> None:
        self._fac = fac

    @ta.overload
    def __call__(self, es: CollectedElements, /, *, parent: T | None = None) -> R: ...

    @ta.overload
    def __call__(self, *es: Elemental, parent: T | None = None) -> R: ...  # noqa

    def __call__(self, arg0, *argv, parent=None):
        ce: CollectedElements
        if isinstance(arg0, CollectedElements):
            check.arg(not argv)
            ce = arg0
        else:
            ce = collect_elements(as_elements(arg0, *argv))
        return self._fac(ce, parent)


##


create_async_injector = _InjectorCreator[AsyncInjector, ta.Awaitable[AsyncInjector]](
    lambda ce, p=None: _injector.create_async_injector(ce, p),
)
