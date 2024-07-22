"""
TODO:
 - 'get current'? -> sniffio..
 - mark whole class / module?
 - sync/greenlet bridge
"""
import abc
import enum
import typing as ta

from .. import lang

if ta.TYPE_CHECKING:
    import asyncio  # noqa
    import sniffio
    import trio  # noqa
    import trio_asyncio
else:
    asyncio = lang.proxy_import('asyncio')
    sniffio = lang.proxy_import('sniffio')
    trio = lang.proxy_import('trio')
    trio_asyncio = lang.proxy_import('trio_asyncio')


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


def get_flavor(obj: ta.Any, default: ta.Union[Flavor, type[_MISSING], None] = _MISSING) -> Flavor:
    u = lang.unwrap_func(obj)

    try:
        return getattr(u, _FLAVOR_ATTR)
    except AttributeError:
        pass

    if (mn := getattr(u, '__module__', None)) is not None:
        if (dp := mn.find('.')) >= 0:
            mn = mn[:dp]
        try:
            return Flavor[mn.upper()]
        except KeyError:
            pass

    if default is not _MISSING:
        return default  # type: ignore
    raise TypeError(f'not marked with flavor: {obj}')


##


class Adapter(lang.Abstract):
    _FROM_METHODS_BY_FLAVOR: ta.ClassVar[ta.Mapping[Flavor, str]] = {
        Flavor.ANYIO: 'from_anyio',
        Flavor.ASYNCIO: 'from_asyncio',
        Flavor.TRIO: 'from_trio',
    }

    def from_(self, fn, fl=None):
        if fl is None:
            fl = get_flavor(fn)
        return getattr(self, self._FROM_METHODS_BY_FLAVOR[fl])(fn)

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
        return trio_asyncio.trio_as_aio(fn)


class TrioAdapter(Adapter):
    def from_asyncio(self, fn):
        return trio_asyncio.aio_as_trio(fn)

    def from_trio(self, fn):
        return fn


_ADAPTERS_BY_BACKEND: ta.Mapping[str, Adapter] = {
    'asyncio': AsyncioAdapter(),
    'trio': TrioAdapter(),
}


def get_adapter() -> Adapter:
    return _ADAPTERS_BY_BACKEND[sniffio.current_async_library()]


def from_anyio(fn):
    return get_adapter().from_anyio(fn)


def from_asyncio(fn):
    return get_adapter().from_asyncio(fn)


def from_trio(fn):
    return get_adapter().from_trio(fn)


def adapt(fn):
    return get_adapter().from_(fn)
