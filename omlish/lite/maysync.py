# ruff: noqa: UP006 UP007 UP043 UP045 UP046 UP047
# @omlish-lite
"""
A system for writing a python function once which can then be effectively used in both sync and async contexts -
including IO, under any (or no) event loop.

Where an 'async fn' returns an 'awaitable', a 'maysync fn' returns a 'maywaitable', which may be `await`'ed in async or
maysync contexts, or passed to `run_maysync` to be run sync.

For example, a maysync function `m_inc_int(x: int) -> int` would be used as such:

 - `run_maysync(m_inc_int(5)) == 6` in sync contexts
 - `assert await m_inc_int(5) == 6` in async and maysync contexts

Maysync fns may be constructed in two ways: either using `make_maysync`, providing an equivalent pair of sync and async
functions, or writing an 'maysync flavored' async python function. 'Maysync flavored' async functions are ones which
only call (await on) other maysync functions - the maysync machinery will ultimately call the appropriate 'leaf' sync or
async functions. Being regular python functions they are free to call whatever they like - for example doing sync IO -
but the point is to, ideally, route all IO through maysync functions such that the maysync code is fully efficiently
usable in any context.

Internally, it's not really correct to say that there is 'no event loop' in the maysync context - rather, each
'entrypoint' call to a maysync fn runs within its own tiny event loop.

===

TODO:
 - ! impl iterators not just generators !
 - __del__
 - (test) maysync context managers
 - CancelledError
 - for debug, mask any running eventloop while running maysync code
 - `[CO_ASYNC_GENERATOR] = {k for k, v in dis.COMPILER_FLAG_NAMES.items() if v == 'ASYNC_GENERATOR'}` ? inspect is big..
  - works down to 3.8
 - make_maysync_from_sync can run with asyncio.run_in_thread
 - make_maysync_from_async can run with asyncio.run_soon
"""
import abc
import inspect
import sys
import threading
import typing as ta

from .abstract import Abstract


T = ta.TypeVar('T')
O = ta.TypeVar('O')
I = ta.TypeVar('I')

_MaysyncX = ta.TypeVar('_MaysyncX')
_MaysyncRS = ta.TypeVar('_MaysyncRS')
_MaysyncRA = ta.TypeVar('_MaysyncRA')


##


class AnyMaysyncFn(Abstract, ta.Generic[_MaysyncRS, _MaysyncRA]):
    def __init__(
            self,
            s: ta.Callable[..., _MaysyncRS],
            a: ta.Callable[..., _MaysyncRA],
    ) -> None:
        if s is None:
            raise TypeError(s)
        if a is None:
            raise TypeError(a)
        self._s, self._a = s, a

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._s!r}, {self._a!r})'

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if hasattr(inspect, 'markcoroutinefunction'):
            inspect.markcoroutinefunction(cls.__call__)

    class FnPair(ta.NamedTuple):
        s: ta.Callable[..., ta.Any]
        a: ta.Callable[..., ta.Any]

    def fn_pair(self) -> ta.Optional[FnPair]:
        return AnyMaysyncFn.FnPair(
            self._s,
            self._a,
        )

    def __get__(self, instance, owner=None):
        return self.__class__(
            self._s.__get__(instance, owner),  # noqa
            self._a.__get__(instance, owner),  # noqa
        )

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


@ta.final
class MaywaitableAlreadyConsumedError(Exception):
    pass


class AnyMaywaitable(Abstract, ta.Generic[_MaysyncX]):
    @ta.final
    def __init__(
            self,
            x: _MaysyncX,
            args: ta.Tuple[ta.Any, ...],
            kwargs: ta.Mapping[str, ta.Any],
    ) -> None:
        self._x, self._args, self._kwargs = x, args, kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._x!r})'


##


@ta.final
class MaysyncFn(AnyMaysyncFn[T, ta.Awaitable[T]], ta.Generic[T]):  # noqa
    def __call__(self, *args, **kwargs):
        return Maywaitable(self, args, kwargs)


@ta.final
class Maywaitable(AnyMaywaitable[MaysyncFn[T]], ta.Awaitable[T]):
    _d: bool = False

    def __run_maysync__(self) -> T:
        if self._d or self._aw is not None:
            raise MaywaitableAlreadyConsumedError(self)

        self._d = True
        return self._x._s(*self._args, **self._kwargs)  # noqa

    #

    _aw: ta.Optional[ta.Awaitable[T]] = None

    def __await__(self) -> ta.Generator[ta.Any, None, T]:
        if (aw := self._aw) is None:
            if self._d:
                raise MaywaitableAlreadyConsumedError(self)

            if _MaysyncThreadLocal.run_context is None:
                aw = self._aw = self._x._a(*self._args, **self._kwargs)  # noqa
            else:
                aw = self._aw = _MaysyncFuture(self)

        return aw.__await__()


##


@ta.final
class MaysyncGeneratorFn(AnyMaysyncFn, ta.Generic[O, I]):  # noqa
    def __call__(self, *args, **kwargs):
        return MaysyncGenerator(self, args, kwargs)


@ta.final
class MaysyncGenerator(AnyMaywaitable[MaysyncGeneratorFn[O, I]], ta.AsyncGenerator[O, I]):
    def _make_sg(self) -> ta.Generator[O, I, None]:
        return self._x._s(*self._args, **self._kwargs)  # noqa

    _sg: ta.Optional[ta.Generator[O, I, None]] = None

    def _get_sg(self) -> ta.Generator[O, I, None]:
        if (sg := self._sg) is None:
            if self._ag is not None:
                raise MaywaitableAlreadyConsumedError(self)
            sg = self._sg = self._make_sg()
        return sg

    def __run_maysync__(self) -> ta.Generator[O, I, None]:
        return (self._sg if self._sg is not None else self._get_sg())

    #

    def _make_ag(self) -> ta.AsyncGenerator[O, I]:
        if _MaysyncThreadLocal.run_context is None:
            return self._x._a(*self._args, **self._kwargs)  # noqa

        async def inner():
            g = self._x._s(*self._args, **self._kwargs)  # noqa

            i: ta.Any = None
            e: ta.Any = None

            while True:
                try:
                    if e is not None:
                        o = g.throw(e)
                    else:
                        o = g.send(i)
                except StopIteration as ex:
                    if ex.value is not None:
                        raise TypeError(ex) from None
                    return

                i = None
                e = None

                try:
                    i = yield o
                except StopIteration as ex:  # noqa
                    raise NotImplementedError  # noqa
                except StopAsyncIteration as ex:  # noqa
                    raise NotImplementedError  # noqa
                except BaseException as ex:  # noqa
                    e = ex

        return inner()

    _ag: ta.Optional[ta.AsyncGenerator[O, I]] = None

    def _get_ag(self) -> ta.AsyncGenerator[O, I]:
        if (ag := self._ag) is None:
            if self._sg is not None:
                raise MaywaitableAlreadyConsumedError(self)
            ag = self._ag = self._make_ag()
        return ag

    def __anext__(self):
        return (self._ag if self._ag is not None else self._get_ag()).__anext__()

    def asend(self, value: I):
        return (self._ag if self._ag is not None else self._get_ag()).asend(value)

    def athrow(self, typ, val=None, tb=None):
        return (self._ag if self._ag is not None else self._get_ag()).athrow(typ, val, tb)

    def aclose(self):
        return (self._ag if self._ag is not None else self._get_ag()).aclose()


##


def make_maysync_fn(
        s: ta.Callable[..., T],
        a: ta.Callable[..., ta.Awaitable[T]],
) -> ta.Callable[..., ta.Awaitable[T]]:
    """Constructs a MaysyncFn from a (sync, async) function pair."""

    return MaysyncFn(s, a)


def make_maysync_generator_fn(
        s: ta.Callable[..., ta.Generator[O, I, None]],
        a: ta.Callable[..., ta.AsyncGenerator[O, I]],
) -> ta.Callable[..., ta.AsyncGenerator[O, I]]:
    """Constructs a MaysyncGeneratorFn from a (sync, async) generator function pair."""

    return MaysyncGeneratorFn(s, a)


@ta.overload
def make_maysync(
        s: ta.Callable[..., T],
        a: ta.Callable[..., ta.Awaitable[T]],
) -> ta.Callable[..., ta.Awaitable[T]]:
    ...


@ta.overload
def make_maysync(
        s: ta.Callable[..., ta.Generator[O, I, None]],
        a: ta.Callable[..., ta.AsyncGenerator[O, I]],
) -> ta.Callable[..., ta.AsyncGenerator[O, I]]:
    ...


def make_maysync(s, a):
    """
    Constructs a MaysyncFn or MaysyncGeneratorFn from a (sync, async) function pair, using `inspect.isasyncgenfunction`
    to determine the type.
    """

    if inspect.isasyncgenfunction(a):
        return MaysyncGeneratorFn(s, a)
    else:
        return MaysyncFn(s, a)


##


@ta.final
class _MaysyncThreadLocal(threading.local):
    run_context: ta.Optional['_MaysyncRunContext'] = None


@ta.final
class _MaysyncRunContext:
    def __init__(self, root: ta.Any) -> None:
        self._root = root

    def run(self, fn: ta.Callable[..., T], *args: ta.Any, **kwargs: ta.Any) -> T:
        prev = _MaysyncThreadLocal.run_context
        _MaysyncThreadLocal.run_context = self

        ph: ta.Any = sys.get_asyncgen_hooks()
        if ph.firstiter is not None or ph.finalizer is not None:
            sys.set_asyncgen_hooks(firstiter=None, finalizer=None)
        else:
            ph = None

        try:
            return fn(*args, **kwargs)

        finally:
            if ph is not None:
                sys.set_asyncgen_hooks(*ph)

            if _MaysyncThreadLocal.run_context is not self:
                raise RuntimeError
            _MaysyncThreadLocal.run_context = prev


def is_running_maysync() -> bool:
    return _MaysyncThreadLocal.run_context is not None


##


@ta.final
class _MaysyncFutureNotAwaitedError(RuntimeError):
    pass


@ta.final
class _MaysyncFuture(ta.Generic[T]):
    def __init__(
            self,
            x: Maywaitable[T],
    ) -> None:
        self._x = x

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._x!r}, done={self.done!r})'

    done: bool = False
    result: T
    error: ta.Optional[BaseException] = None

    def __await__(self) -> ta.Generator['_MaysyncFuture', None, T]:
        if not self.done:
            yield self
        if not self.done:
            raise _MaysyncFutureNotAwaitedError
        if self.error is not None:
            raise self.error
        else:
            return self.result

    def s(self) -> None:
        if self.done:
            return

        try:
            self.result = self._x._x._s(*self._x._args, **self._x._kwargs)  # noqa
        except BaseException as ex:  # noqa
            self.error = ex
        self.done = True

    async def a(self) -> None:
        if self.done:
            return

        try:
            self.result = await self._x._x._a(*self._x._args, **self._x._kwargs)  # noqa
        except BaseException as ex:  # noqa
            self.error = ex
        self.done = True


##


@ta.final
class _MaysyncDriver:
    def __init__(
            self,
            ctx: _MaysyncRunContext,
            coro: ta.Any,
    ) -> None:
        self.ctx, self.coro = ctx, coro

    value: ta.Any

    def __iter__(self) -> ta.Generator['_MaysyncFuture', None, None]:
        try:
            a = self.coro.__await__()
            try:
                g = iter(a)
                try:
                    while True:
                        try:
                            f = self.ctx.run(g.send, None)
                        except StopIteration as ex:
                            self.value = ex.value
                            return

                        if not isinstance(f, _MaysyncFuture):
                            raise TypeError(f)

                        yield f
                        del f

                finally:
                    if g is not a:
                        self.ctx.run(g.close)

            finally:
                self.ctx.run(a.close)

        finally:
            self.ctx.run(self.coro.close)


##


def run_maysync_fn(
        m: ta.Awaitable[T],
) -> T:
    if isinstance(m, Maywaitable):
        return m.__run_maysync__()

    for f in (drv := _MaysyncDriver(_MaysyncRunContext(m), m)):
        f.s()
        del f

    return drv.value


def run_maysync_generator_fn(
        m: ta.AsyncGenerator[O, I],
) -> ta.Generator[O, I, None]:
    if isinstance(m, MaysyncGenerator):
        return m.__run_maysync__()

    def inner():
        ctx = _MaysyncRunContext(m)

        try:
            i: ta.Any = None
            e: ta.Any = None

            while True:
                if e is not None:
                    coro = m.athrow(e)
                else:
                    coro = m.asend(i)

                i = None
                e = None

                drv = _MaysyncDriver(ctx, coro)
                di = iter(drv)
                try:
                    while True:
                        try:
                            f = next(di)
                        except StopAsyncIteration:
                            return
                        except StopIteration:
                            break

                        f.s()
                        del f

                finally:
                    di.close()

                o = drv.value
                try:
                    i = yield o
                except BaseException as ex:  # noqa
                    e = ex

        finally:
            for f in _MaysyncDriver(ctx, m.aclose()):
                f.s()

    return inner()


@ta.overload
def run_maysync(
        m: ta.Awaitable[T],
) -> T:
    ...


@ta.overload
def run_maysync(
        m: ta.AsyncGenerator[O, I],
) -> ta.Generator[O, I, None]:
    ...


def run_maysync(m):
    if hasattr(m, '__await__'):
        return run_maysync_fn(m)
    elif hasattr(m, '__aiter__'):
        return run_maysync_generator_fn(m)
    else:
        raise TypeError(m)


##


@ta.final
class RunMaysyncContextManager(ta.Generic[T]):
    def __init__(self, acm: ta.AsyncContextManager[T]) -> None:
        self._acm = acm

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._acm!r})'

    def __enter__(self) -> T:
        return run_maysync(self._acm.__aenter__())

    def __exit__(self, exc_type, exc_val, exc_tb):
        return run_maysync(self._acm.__aexit__(exc_type, exc_val, exc_tb))


run_maysync_context_manager = RunMaysyncContextManager


##


_MAYSYNC_MARK_ATTR = '__maysync__'


def mark_maysync(o):
    if not callable(o) or isinstance(o, AnyMaysyncFn):
        raise TypeError(o)
    setattr(o, _MAYSYNC_MARK_ATTR, True)
    return o


def is_maysync(o: ta.Any) -> bool:
    return isinstance(o, AnyMaysyncFn) or getattr(o, _MAYSYNC_MARK_ATTR, False)


mark_maysync(AnyMaysyncFn)
