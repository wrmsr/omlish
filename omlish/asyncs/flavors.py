"""
TODO:
 - 'get current'? -> sniffio..
 - mark whole class / module?
 - sync/greenlet bridge
 - auto for things in asyncio/trio/anyio packages
"""
import enum
import typing as ta

from .. import lang

if ta.TYPE_CHECKING:
    import asyncio
    import sniffio
    import trio
    import trio_asyncio
else:
    asyncio = lang.proxy_import('asyncio')
    sniffio = lang.proxy_import('sniffio')
    trio = lang.proxy_import('trio')
    trio_asyncio = lang.proxy_import('trio_asyncio')


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
    if default is not _MISSING:
        return default  # type: ignore
    raise TypeError(f'not marked with flavor: {obj}')
