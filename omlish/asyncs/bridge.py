"""
https://github.com/kubernetes/kubernetes/blob/60c4c2b2521fb454ce69dee737e3eb91a25e0535/pkg/controller/volume/persistentvolume/pv_controller.go#L60-L63

==================================================================
PLEASE DO NOT ATTEMPT TO SIMPLIFY THIS CODE.
KEEP THE SPACE SHUTTLE FLYING.
==================================================================

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


def trivial_s_to_a(fn):
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)
    return inner


def trivial_a_to_s(fn):
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
        # breakpoint()


#


_DEBUG_PRINT: ta.Callable[..., None] | None = None
# _DEBUG_PRINT = print  # noqa

_TRACK_TRANSITION_OBJS = False


#


_BRIDGE_TRANSITIONS_SEQ = itertools.count()


class _BridgeTransition(ta.NamedTuple):
    seq: int
    a_to_s: bool

    obj_cls: type
    obj_id: int

    obj: ta.Any


def _make_transition(seq: int, a_to_s: bool, obj: ta.Any) -> _BridgeTransition:
    return _BridgeTransition(seq, a_to_s, obj.__class__, id(obj), (obj if _TRACK_TRANSITION_OBJS else None))


_BRIDGED_TASKS: ta.MutableMapping[ta.Any, list[_BridgeTransition]] = weakref.WeakKeyDictionary()

_BRIDGE_GREENLET_ATTR = f'__{__package__.replace(".", "__")}__bridge_greenlet__'


def _push_transition(a_to_s: bool, l: list[_BridgeTransition], t: _BridgeTransition) -> _BridgeTransition:
    l.append(t)
    if _DEBUG_PRINT:
        _DEBUG_PRINT(f'_push_transition: {a_to_s=} {id(l)=} {t=}')
    return t


def _pop_transition(a_to_s: bool, l: list[_BridgeTransition]) -> _BridgeTransition:
    t = l.pop()
    if _DEBUG_PRINT:
        _DEBUG_PRINT(f'_pop_transition: {a_to_s=} {id(l)=} {t=}')
    return t


def _get_transitions() -> list[_BridgeTransition]:
    l: list[_BridgeTransition] = []

    if (t := aiu.get_current_backend_task()) is not None:
        try:
            tl = _BRIDGED_TASKS[t]
        except KeyError:
            pass
        else:
            l.extend(tl)

    g = greenlet.getcurrent()
    try:
        gl = getattr(g, _BRIDGE_GREENLET_ATTR)
    except AttributeError:
        pass
    else:
        l.extend(gl)

    l.sort(key=lambda t: (t.seq, t.a_to_s))
    return l


def is_in_bridge() -> bool:
    if _DEBUG_PRINT:
        _DEBUG_PRINT(_get_transitions())

    if (t := aiu.get_current_backend_task()) is not None:
        try:
            tl = _BRIDGED_TASKS[t]
        except KeyError:
            last_t = None
        else:
            if tl:
                last_t = tl[-1]
            else:
                last_t = None
    else:
        last_t = None

    g = greenlet.getcurrent()
    try:
        gl = getattr(g, _BRIDGE_GREENLET_ATTR)
    except AttributeError:
        last_g = None
    else:
        if gl:
            last_g = gl[-1]
        else:
            last_g = None

    if last_t is None:
        if last_g is None:
            return False
        o = last_g
    else:  # noqa
        if last_g is None or last_g.seq < last_t.seq:
            o = last_t
        else:
            o = last_g

    in_a = (t is not None)

    if _DEBUG_PRINT:
        _DEBUG_PRINT(f'{o.a_to_s=} {in_a=}')

    return in_a != o.a_to_s


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
                if (cur_g := _pop_transition(False, gl)) is not added_g:  # noqa
                    raise UnexpectedBridgeNestingError
                if gl:
                    raise UnexpectedBridgeNestingError

        seq = next(_BRIDGE_TRANSITIONS_SEQ)

        g = greenlet.greenlet(inner)
        setattr(g, _BRIDGE_GREENLET_ATTR, gl := [])  # type: ignore
        added_g = _push_transition(False, gl, _make_transition(seq, False, g))

        if (t := aiu.get_current_backend_task()) is not None:
            try:
                tl = _BRIDGED_TASKS[t]
            except KeyError:
                tl = _BRIDGED_TASKS[t] = []
            added_t = _push_transition(False, tl, _make_transition(seq, False, g))

        try:
            result: ta.Any = g.switch()
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
                if (cur_t := _pop_transition(False, tl)) is not added_t:  # noqa
                    raise UnexpectedBridgeNestingError

    return outer


def a_to_s(fn):
    def inner(*args, **kwargs):
        seq = next(_BRIDGE_TRANSITIONS_SEQ)

        if (t := aiu.get_current_backend_task()) is not None:
            try:
                tl = _BRIDGED_TASKS[t]
            except KeyError:
                tl = _BRIDGED_TASKS[t] = []
            added_t = _push_transition(True, tl, _make_transition(seq, True, t))
        else:
            added_t = None

        g = greenlet.getcurrent()
        try:
            gl = getattr(g, _BRIDGE_GREENLET_ATTR)
        except AttributeError:
            setattr(g, _BRIDGE_GREENLET_ATTR, gl := [])
        added_g = _push_transition(True, gl, _make_transition(seq, True, g))

        try:
            ret = missing = object()

            async def gate():
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

        finally:
            if t is not None:
                if (tl2 := _BRIDGED_TASKS[t]) is not tl:  # noqa
                    raise UnexpectedBridgeNestingError
                if (cur_t := _pop_transition(True, tl)) is not added_t:  # noqa
                    raise UnexpectedBridgeNestingError

            if (gl2 := getattr(g, _BRIDGE_GREENLET_ATTR)) is not gl:  # noqa
                raise UnexpectedBridgeNestingError
            if (cur_g := _pop_transition(True, gl)) is not added_g:  # noqa
                raise UnexpectedBridgeNestingError

        return ret

    return inner
