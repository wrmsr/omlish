"""
https://github.com/kubernetes/kubernetes/blob/60c4c2b2521fb454ce69dee737e3eb91a25e0535/pkg/controller/volume/persistentvolume/pv_controller.go#L60-L63

==================================================================
PLEASE DO NOT ATTEMPT TO SIMPLIFY THIS CODE.
KEEP THE SPACE SHUTTLE FLYING.
==================================================================

TODO:
 - reuse greenlet if nested somehow?
 - test cancel

See:
 - https://github.com/sqlalchemy/sqlalchemy/blob/21ea01eebe0350ad1185c7288dca61f363ebd2fe/lib/sqlalchemy/util/concurrency.py
   - ( https://gist.github.com/snaury/202bf4f22c41ca34e56297bae5f33fef )
   - Baked into sqlalchemy and hard-bound to asyncio.
 - https://github.com/oremanj/greenback/blob/ca69b023a9b7b58b715f3b1d78fc116e788a2c9f/greenback/_impl.py
   - ( https://gist.github.com/oremanj/f18ef3e55b9487c2e93eee42232583f2 )
   - Similar to this, but does horrible things with ctypes and is hard-bound to greenlet.
 - https://github.com/fastapi/asyncer/blob/2a4b8ef2540ec687af13d3f361c4ed0cf0cb624d/asyncer/_main.py
 - https://github.com/django/asgiref/blob/05ae3eee3fae4005ae4cfb0bb22d281725fabade/asgiref/sync.py
   - Both are much heavier weight and hard-bound to threads.
"""  # noqa
import functools  # noqa
import itertools
import sys  # noqa
import types
import typing as ta
import weakref

from .. import check
from .. import lang
from .. import sync
from ..concurrent import threadlets
from .sync import sync_await


if ta.TYPE_CHECKING:
    import asyncio

    from . import anyio as aiu

else:
    asyncio = lang.proxy_import('asyncio')

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


_THREADLETS_IMPL = threadlets.GreenletThreadlets
# from ..concurrent.tests.real import RealThreadlets
# _THREADLETS_IMPL = RealThreadlets

_THREADLETS = sync.LazyFn(lambda: _THREADLETS_IMPL())


def _threadlets() -> threadlets.Threadlets:
    return _THREADLETS.get()


#


class BridgeAwaitRequiredError(Exception):
    pass


class MissingBridgeThreadletError(Exception):
    pass


class UnexpectedBridgeNestingError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # breakpoint()


#


_DEBUG_PRINT: ta.Callable[..., None] | None = None
# _DEBUG_PRINT = functools.partial(print, file=sys.stderr)  # noqa

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

_BRIDGE_THREADLET_ATTR = f'__{__package__.replace(".", "__")}__bridge_threadlet__'


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

    g = _threadlets().get_current()
    try:
        gl = getattr(g.underlying, _BRIDGE_THREADLET_ATTR)
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

    g = _threadlets().get_current()
    try:
        gl = getattr(g.underlying, _BRIDGE_THREADLET_ATTR)
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
    g = _threadlets().get_current()

    if not getattr(g.underlying, _BRIDGE_THREADLET_ATTR, False):
        _safe_cancel_awaitable(awaitable)
        raise MissingBridgeThreadletError

    return check.not_none(g.parent).switch(awaitable)


def s_to_a(fn, *, require_await=False):
    @types.coroutine
    def outer(*args, **kwargs):
        def inner():
            try:
                return fn(*args, **kwargs)
            finally:
                if (gl2 := getattr(g.underlying, _BRIDGE_THREADLET_ATTR)) is not gl:  # noqa
                    raise UnexpectedBridgeNestingError
                if (cur_g := _pop_transition(False, gl)) is not added_g:  # noqa
                    raise UnexpectedBridgeNestingError
                if gl:
                    raise UnexpectedBridgeNestingError

        seq = next(_BRIDGE_TRANSITIONS_SEQ)

        g = _threadlets().spawn(inner)
        setattr(g.underlying, _BRIDGE_THREADLET_ATTR, gl := [])  # type: ignore
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
                except BaseException as e:  # noqa
                    result = g.throw(e)
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

        g = _threadlets().get_current()
        try:
            gl = getattr(g.underlying, _BRIDGE_THREADLET_ATTR)
        except AttributeError:
            setattr(g.underlying, _BRIDGE_THREADLET_ATTR, gl := [])
        added_g = _push_transition(True, gl, _make_transition(seq, True, g))

        try:
            ret = missing = object()

            async def gate():
                nonlocal ret
                ret = await fn(*args, **kwargs)

            cr = gate()
            sv = None
            he = False
            try:
                while True:
                    if not he:
                        try:
                            sv = cr.send(sv)
                        except StopIteration:
                            break
                    he = False

                    if ret is missing or cr.cr_await is not None or cr.cr_running:
                        try:
                            sv = s_to_a_await(sv)  # type: ignore
                        except BaseException as e:  # noqa
                            sv = cr.throw(e)
                            he = True

            finally:
                cr.close()

        finally:
            if t is not None:
                if (tl2 := _BRIDGED_TASKS[t]) is not tl:  # noqa
                    raise UnexpectedBridgeNestingError
                if (cur_t := _pop_transition(True, tl)) is not added_t:  # noqa
                    raise UnexpectedBridgeNestingError

            if (gl2 := getattr(g.underlying, _BRIDGE_THREADLET_ATTR)) is not gl:  # noqa
                raise UnexpectedBridgeNestingError
            if (cur_g := _pop_transition(True, gl)) is not added_g:  # noqa
                raise UnexpectedBridgeNestingError

        return ret

    return inner
