"""
TODO:
 - reuse greenlet if nested somehow?
"""
import sys
import types
import typing as ta
import weakref

from .. import lang
from .asyncs import sync_await


if ta.TYPE_CHECKING:
    import asyncio

    import greenlet

    from . import anyio as aiu

else:
    asyncio = lang.proxy_import('asyncio')

    greenlet = lang.proxy_import('greenlet')

    aiu = lang.proxy_import('.anyio', __package__)


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


class UnexpectedBridgeNestingError(Exception):
    pass


# _DEBUG_PRINT = None
_DEBUG_PRINT = print

_BRIDGED_TASKS = weakref.WeakSet()


def is_in_bridge() -> bool:
    has_t = (t := aiu.get_current_backend_task()) is not None
    has_tb = t is not None and t in _BRIDGED_TASKS
    has_gl = getattr(greenlet.getcurrent(), _BRIDGE_GREENLET_ATTR, False)
    if _DEBUG_PRINT:
        _DEBUG_PRINT(f'{has_t=} {has_tb=} {has_gl=}')
    return has_gl


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


def a_to_s(fn):
    def inner(*args, **kwargs):
        ret = missing = object()

        async def gate():
            t = aiu.get_current_backend_task()
            added_t = False
            added_g = False
            if t is None:
                g = greenlet.getcurrent()
                if not getattr(g, _BRIDGE_GREENLET_ATTR, False):
                    added_g = True
                    setattr(g, _BRIDGE_GREENLET_ATTR, True)
                    if _DEBUG_PRINT:
                        _DEBUG_PRINT(f'added g {g=}')
                else:
                    if _DEBUG_PRINT:
                        _DEBUG_PRINT(f'didnt add g {g=}')
            else:
                g = None
                if t not in _BRIDGED_TASKS:
                    added_t = True
                    _BRIDGED_TASKS.add(t)
                    if _DEBUG_PRINT:
                        _DEBUG_PRINT(f'added t {t=}')
                else:
                    if _DEBUG_PRINT:
                        _DEBUG_PRINT(f'didnt add t {t=}')

            try:
                nonlocal ret
                ret = await fn(*args, **kwargs)

            finally:
                if added_g:
                    if not getattr(g, _BRIDGE_GREENLET_ATTR, False):
                        raise UnexpectedBridgeNestingError
                    else:
                        delattr(g, _BRIDGE_GREENLET_ATTR)
                        if _DEBUG_PRINT:
                            _DEBUG_PRINT(f'removed g {g=}')
                elif g is not None:
                    if not getattr(g, _BRIDGE_GREENLET_ATTR, False):
                        raise UnexpectedBridgeNestingError
                    if _DEBUG_PRINT:
                        _DEBUG_PRINT(f'didnt remove g {g=}')

                if added_t:
                    if t not in _BRIDGED_TASKS:
                        raise UnexpectedBridgeNestingError
                    _BRIDGED_TASKS.remove(t)
                    if _DEBUG_PRINT:
                        _DEBUG_PRINT(f'removed t {t=}')
                elif t is not None:
                    if t not in _BRIDGED_TASKS:
                        raise UnexpectedBridgeNestingError
                    if _DEBUG_PRINT:
                        _DEBUG_PRINT(f'didnt remove t {t=}')

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
