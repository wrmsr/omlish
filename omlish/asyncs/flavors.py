"""
TODO:
 - 'get current'? -> sniffio..
 - mark whole class / module?
 - sync/greenlet bridge
"""
import abc
import dataclasses as dc
import enum
import functools
import typing as ta

from .. import lang
from .trio_asyncio import check_trio_asyncio
from .trio_asyncio import with_trio_asyncio_loop


if ta.TYPE_CHECKING:
    import sniffio
    import trio_asyncio
else:
    sniffio = lang.proxy_import('sniffio')
    trio_asyncio = lang.proxy_import('trio_asyncio')


T = ta.TypeVar('T')


##


_FLAVOR_ATTR = '__async_flavor__'


class _MISSING(lang.Marker):
    pass


class Flavor(enum.Enum):
    ASYNCIO = enum.auto()
    TRIO = enum.auto()
    ANYIO = enum.auto()


def mark_flavor(f: Flavor):
    if not isinstance(f, Flavor):
        raise TypeError(f)

    def inner(fn):
        setattr(fn, _FLAVOR_ATTR, f)
        return fn

    return inner


mark_asyncio = mark_flavor(Flavor.ASYNCIO)
mark_anyio = mark_flavor(Flavor.ANYIO)
mark_trio = mark_flavor(Flavor.TRIO)

PACKAGE_FLAVORS: ta.MutableMapping[str, Flavor] = {
    'anyio': Flavor.ANYIO,
    'asyncio': Flavor.ASYNCIO,
    'trio': Flavor.TRIO,

    'sqlalchemy.ext.asyncio': Flavor.ASYNCIO,
}

_MODULE_FLAVOR_CACHE: dict[str, Flavor | None] = {}


def _get_module_flavor(p: str) -> Flavor | None:
    try:
        return _MODULE_FLAVOR_CACHE[p]
    except KeyError:
        pass
    pf: Flavor | None = None
    for cp, cf in PACKAGE_FLAVORS.items():
        if p.startswith(cp) and (len(cp) == len(p) or p[len(cp)] == '.'):
            pf = cf
            break
    _MODULE_FLAVOR_CACHE[p] = pf
    return pf


def get_flavor(obj: ta.Any, default: Flavor | type[_MISSING] | None = _MISSING) -> Flavor:
    u = lang.unwrap_func(obj)

    try:
        return getattr(u, _FLAVOR_ATTR)
    except AttributeError:
        pass

    if (mn := getattr(u, '__module__', None)) is not None:
        if (pf := _get_module_flavor(mn)):
            return pf

    if default is not _MISSING:
        return default  # type: ignore

    raise TypeError(f'not marked with flavor: {obj}')


##


def with_adapter_loop(*, wait=False):
    def outer(fn):
        @functools.wraps(fn)
        async def inner(*args, **kwargs):
            cur_lib = sniffio.current_async_library()

            if cur_lib == 'asyncio':
                await fn(*args, **kwargs)

            elif cur_lib == 'trio':
                await with_trio_asyncio_loop(wait=wait)(fn)(*args, **kwargs)

            else:
                raise RuntimeError(f'Unknown async library: {cur_lib}')

        return inner

    return outer


##


class Adapter(lang.Abstract):
    _FROM_METHODS_BY_FLAVOR: ta.ClassVar[ta.Mapping[Flavor, str]] = {
        Flavor.ANYIO: 'from_anyio',
        Flavor.ASYNCIO: 'from_asyncio',
        Flavor.TRIO: 'from_trio',
    }

    def adapt(self, fn, fl=None):
        if fl is None:
            fl = get_flavor(fn)
        return getattr(self, self._FROM_METHODS_BY_FLAVOR[fl])(fn)

    #

    def from_anyio(self, fn):
        return fn

    @abc.abstractmethod
    def from_asyncio(self, fn):
        raise NotImplementedError

    @abc.abstractmethod
    def from_trio(self, fn):
        raise NotImplementedError


class AsyncioAdapter(Adapter):
    def from_asyncio(self, fn):
        return fn

    def from_trio(self, fn):
        check_trio_asyncio()
        return trio_asyncio.trio_as_aio(fn)


class TrioAdapter(Adapter):
    def from_asyncio(self, fn):
        check_trio_asyncio()
        return trio_asyncio.aio_as_trio(fn)

    def from_trio(self, fn):
        return fn


_ADAPTERS_BY_BACKEND: ta.Mapping[str, Adapter] = {
    'asyncio': AsyncioAdapter(),
    'trio': TrioAdapter(),
}


def get_adapter() -> Adapter:
    return _ADAPTERS_BY_BACKEND[sniffio.current_async_library()]


def adapt(fn, fl=None):
    return get_adapter().adapt(fn, fl)


def from_anyio(fn):
    return get_adapter().from_anyio(fn)


def from_asyncio(fn):
    return get_adapter().from_asyncio(fn)


def from_trio(fn):
    return get_adapter().from_trio(fn)


##


@dc.dataclass(frozen=True)
class ContextManagerAdapter(ta.Generic[T]):
    obj: ta.AsyncContextManager[T]
    adapt: ta.Callable[[ta.Callable], ta.Callable]

    async def __aenter__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        return await self.adapt(self.obj.__aenter__)(*args, **kwargs)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.adapt(self.obj.__aexit__)(exc_type, exc_val, exc_tb)


def adapt_context(obj):
    return ContextManagerAdapter(obj, get_adapter().adapt)


def from_anyio_context(obj):
    return ContextManagerAdapter(obj, get_adapter().from_anyio)


def from_asyncio_context(obj):
    return ContextManagerAdapter(obj, get_adapter().from_asyncio)


def from_trio_context(obj):
    return ContextManagerAdapter(obj, get_adapter().from_trio)
