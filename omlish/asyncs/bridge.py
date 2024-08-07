"""
TODO:
 - reuse greenlet if nested somehow?
"""
import itertools
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


class BridgeAwaitRequiredError(Exception):
    pass


class MissingBridgeGreenletError(Exception):
    pass


class UnexpectedBridgeNestingError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        breakpoint()


_BRIDGE_TRANSITIONS_SEQ = itertools.count()


class _BridgeTransition(ta.NamedTuple):
    obj: ta.Any
    seq: int
    a_to_s: bool


_BRIDGED_TASKS: ta.MutableMapping[ta.Any, list[_BridgeTransition]] = weakref.WeakKeyDictionary()

_BRIDGE_GREENLET_ATTR = f'__{__package__.replace(".", "__")}__bridge_greenlet__'


def is_in_bridge() -> bool:
    # has_t = (t := aiu.get_current_backend_task()) is not None
    # has_tb = t is not None and t in _BRIDGED_TASKS
    # has_g = getattr(greenlet.getcurrent(), _BRIDGE_GREENLET_ATTR, False)
    # print(f'{has_t=} {has_tb=} {has_g=}')
    # return has_g
    # raise NotImplementedError
    return False


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
    def outer(*args, **kwargs):
        def inner():
            try:
                return fn(*args, **kwargs)
            finally:
                if (gl2 := getattr(g, _BRIDGE_GREENLET_ATTR)) is not gl:  # noqa
                    raise UnexpectedBridgeNestingError
                if (cur_g := gl.pop()) is not added_g:  # noqa
                    raise UnexpectedBridgeNestingError
                if gl:
                    raise UnexpectedBridgeNestingError

        seq = next(_BRIDGE_TRANSITIONS_SEQ)

        g = greenlet.greenlet(inner)
        setattr(g, _BRIDGE_GREENLET_ATTR, gl := [])
        gl.append(added_g := _BridgeTransition(g, seq, False))

        if (t := aiu.get_current_backend_task()) is not None:
            try:
                tl = _BRIDGED_TASKS[t]
            except KeyError:
                tl = _BRIDGED_TASKS[t] = []
            tl.append(added_t := _BridgeTransition(t, seq, False))

        try:
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

        finally:
            if t is not None:
                if (tl2 := _BRIDGED_TASKS[t]) is not tl:  # noqa
                    raise UnexpectedBridgeNestingError
                if (cur_t := tl.pop()) is not added_t:  # noqa
                    raise UnexpectedBridgeNestingError

    return outer


def a_to_s(fn):
    def inner(*args, **kwargs):
        ret = missing = object()

        async def gate():
            seq = next(_BRIDGE_TRANSITIONS_SEQ)

            if (t := aiu.get_current_backend_task()) is not None:
                try:
                    tl = _BRIDGED_TASKS[t]
                except KeyError:
                    tl = _BRIDGED_TASKS[t] = []
                tl.append(added_t := _BridgeTransition(t, seq, True))
            else:
                added_t = None

            g = greenlet.getcurrent()
            try:
                gl = getattr(_BRIDGE_GREENLET_ATTR)
            except AttributeError:
                added_g = None
            else:
                gl.append(added_g := _BridgeTransition(g, seq, True))

            if not (added_t or added_g):
                raise UnexpectedBridgeNestingError

            try:
                nonlocal ret
                ret = await fn(*args, **kwargs)

            finally:
                if t is not None:
                    if (tl2 := _BRIDGED_TASKS[t]) is not tl:  # noqa
                        raise UnexpectedBridgeNestingError
                    if (cur_t := tl.pop()) is not added_t:  # noqa
                        raise UnexpectedBridgeNestingError

                if added_g is not None:
                    if (gl2 := getattr(g, _BRIDGE_GREENLET_ATTR)) is not gl:  # noqa
                        raise UnexpectedBridgeNestingError
                    if (cur_g := gl.pop()) is not added_g:  # noqa
                        raise UnexpectedBridgeNestingError

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
