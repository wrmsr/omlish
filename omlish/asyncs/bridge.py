"""
TODO:
 - reuse greenlet if nested somehow?
"""
import sys
import types
import typing as ta

from .. import lang
from .asyncs import sync_await


if ta.TYPE_CHECKING:
    import asyncio

    import anyio
    import greenlet
    import sniffio

else:
    asyncio = lang.proxy_import('asyncio')

    anyio = lang.proxy_import('anyio')
    greenlet = lang.proxy_import('greenlet')
    sniffio = lang.proxy_import('sniffio')


T = ta.TypeVar('T')


##


def simple_s_to_a(fn):
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)
    return inner


def simple_a_to_s(fn):
    def inner(*args, **kwargs):
        return sync_await(fn, *args, **kwargs)
    return inner


##
# https://gist.github.com/snaury/202bf4f22c41ca34e56297bae5f33fef


_BRIDGE_GREENLET_ATTR = f'__{__package__.replace(".", "__")}__bridge_greenlet__'


class BridgeAwaitRequiredError(Exception):
    pass


class MissingBridgeGreenletError(Exception):
    pass


def is_in_s_to_a_bridge() -> bool:
    return getattr(greenlet.getcurrent(), _BRIDGE_GREENLET_ATTR, False)


def _safe_cancel_awaitable(awaitable: ta.Awaitable[ta.Any]) -> None:
    # https://docs.python.org/3/reference/datamodel.html#coroutine.close
    if asyncio.iscoroutine(awaitable):
        awaitable.close()  # noqa


def s_to_a_await(awaitable: ta.Awaitable[T]) -> T:
    g = greenlet.getcurrent()

    if not getattr(g, _BRIDGE_GREENLET_ATTR, False):
        _safe_cancel_awaitable(awaitable)
        raise MissingBridgeGreenletError

    return g.parent.switch(awaitable)


def s_to_a(fn, *, require_await=False):
    @types.coroutine
    def inner(*args, **kwargs):
        g = greenlet.greenlet(fn)
        setattr(g, _BRIDGE_GREENLET_ATTR, True)

        result: ta.Any = g.switch(*args, **kwargs)
        switch_occurred = False
        while not g.dead:
            switch_occurred = True
            try:
                value = yield result
            except BaseException:  # noqa
                result = g.throw(*sys.exc_info())
            else:
                result = g.switch(value)

        if require_await and not switch_occurred:
            raise BridgeAwaitRequiredError

        return result

    return inner


##


_BRIDGE_TASK_ATTR = f'__{__package__.replace(".", "__")}__bridge_task__'


def is_in_a_to_s_bridge() -> bool:
    try:
        ct = anyio.get_current_task()
    except sniffio.AsyncLibraryNotFoundError:
        return False
    return getattr(ct, _BRIDGE_TASK_ATTR, False)


def a_to_s(fn):
    def inner(*args, **kwargs):
        ret = missing = object()

        async def gate():
            ct = anyio.get_current_task()
            setattr(ct, _BRIDGE_TASK_ATTR, False)

            nonlocal ret
            ret = await fn(*args, **kwargs)

        cr = gate()
        sv = None
        try:
            while True:
                try:
                    sv = cr.send(sv)
                except StopIteration:
                    break

                if ret is missing or cr.cr_await is not None or cr.cr_running:
                    sv = s_to_a_await(sv)

        finally:
            cr.close()

        return ret

    return inner


##


def is_in_bridge() -> bool:
    return is_in_s_to_a_bridge() or is_in_a_to_s_bridge()
