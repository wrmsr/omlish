# ruff: noqa: UP006 UP043 UP045 UP046 UP047
# @omlish-lite
"""
A system for writing a python function once which can then be effectively used in both sync and async contexts -
including IO, under any (or no) event loop.

Where an 'async fn' returns an 'awaitable', a 'maysync fn' returns a 'maywaitable', which is an object with two
nullary methods:

 - `def s()` - to be called in sync contexts
 - `async def a()` - to be called in async and maysync contexts

For example, a maysync function `m_inc_int(x: int) -> int` would be used as such:

 - `assert m_inc_int(5).s() == 6` in sync contexts
 - `assert await m_inc_int(5).a() == 6` in async and maysync contexts

Maysync fns may be constructed in two ways: either using `make_maysync`, providing an equivalent pair of sync and async
functions, or using the `@maysync` decorator to wrap a 'maysync flavored' async function. 'Maysync flavored' async
functions are ones which only call other maysync functions through their 'maysync context' - that is, they  use the 'a'
methods on maywaitables - for example: `await m_foo().a()` - and the maysync machinery will ultimately call the
appropriate 'leaf' sync or async functions. Being regular python functions they are free to call whatever they like -
for example doing sync IO - but the point is to, ideally, route all IO through maysync functions such that the maysync
code is fully efficiently usable in any context.

Internally, it's not really correct to say that there is 'no event loop' in the maysync context - rather, each
'entrypoint' call to a maysync fn runs within its own tiny event loop.

===

TODO:
 - __del__
 - (test) maysync context managers
 - CancelledError
 - for debug, mask any running eventloop while running maysync code
 - `[CO_ASYNC_GENERATOR] = {k for k, v in dis.COMPILER_FLAG_NAMES.items() if v == 'ASYNC_GENERATOR'}` ? inspect is big..
  - works down to 3.8
 - make_maysync_from_sync can run with asyncio.run_in_thread
 - make_maysync_from_async can run with asyncio.run_soon
 - elide redundant close/aclose for known cpy machinery
"""
import abc
import functools
import inspect
import sys
import threading
import typing as ta


T = ta.TypeVar('T')
T_co = ta.TypeVar('T_co', covariant=True)

O = ta.TypeVar('O')
O_co = ta.TypeVar('O_co', covariant=True)

I = ta.TypeVar('I')
I_contra = ta.TypeVar('I_contra', contravariant=True)

_MaysyncX = ta.TypeVar('_MaysyncX')

_MaysyncRS = ta.TypeVar('_MaysyncRS')
_MaysyncRA = ta.TypeVar('_MaysyncRA')


##


class Maywaitable(ta.Protocol[T_co]):
    """
    The maysync version of `Awaitable[T]`. Non-generator maysync functions return a `Maywaitable`, with the following
    nullary methods:

     - `def s()` - to be called in sync contexts
     - `async def a()` - to be called in async and maysync contexts

    Only the proper method should be called in each context.
    """

    def s(self) -> T_co:
        ...

    def a(self) -> ta.Awaitable[T_co]:
        ...


class MaysyncGenerator(ta.Protocol[O_co, I_contra]):
    """
    The maysync version of `AsyncGenerator[O, I]`. Generator maysync functions return a `MaysyncGenerator`, with the
    following methods:

     - `def s()` - to be called in sync contexts
     - `async def a()` - to be called in async and maysync contexts

    Only the proper method should be called in each context.
    """

    def s(self) -> ta.Generator[O_co, I_contra, None]:
        ...

    def a(self) -> ta.AsyncGenerator[O_co, I_contra]:
        ...


# The maysync equivalent of an async function
MaysyncFn = ta.Callable[..., Maywaitable[T]]  # ta.TypeAlias  # omlish-amalg-typing-no-move

# The maysync equivalent of an async generator function
MaysyncGeneratorFn = ta.Callable[..., MaysyncGenerator[O, I]]  # ta.TypeAlias  # omlish-amalg-typing-no-move


class Maysync_(abc.ABC):  # noqa
    """
    Abstract base class for maysync objects - either MaysyncFn's or MaysyncGeneratorFn's.

    The concrete implementations are module-level implementation detail, and in general users should make a point to
    only interact with the protocols defined above, but introspection can be necessary at times.
    """

    def __init_subclass__(cls, **kwargs):
        if Maysync_ in cls.__bases__ and abc.ABC not in cls.__bases__:
            raise TypeError(cls)

        super().__init_subclass__(**kwargs)

    class FnPair(ta.NamedTuple):
        s: ta.Callable[..., ta.Any]
        a: ta.Callable[..., ta.Any]

    @abc.abstractmethod
    def fn_pair(self) -> ta.Optional[FnPair]:
        """If this maysync object is backed by a (sync, async) pair of functions, returns the pair."""

        raise NotImplementedError

    @abc.abstractmethod
    def cast(self):
        pass

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class MaysyncFn_(Maysync_, abc.ABC, ta.Generic[T]):  # noqa
    @ta.final
    def cast(self) -> MaysyncFn[T]:
        return ta.cast('MaysyncFn[T]', self)


class MaysyncGeneratorFn_(Maysync_, abc.ABC, ta.Generic[O, I]):  # noqa
    @ta.final
    def cast(self) -> MaysyncGenerator[O, I]:
        return ta.cast('MaysyncGenerator[O, I]', self)


##


class _MaysyncThreadLocal(threading.local):
    context: ta.Optional['_MaysyncContext'] = None


class _MaysyncContext(abc.ABC):
    mode: ta.ClassVar[ta.Literal['s', 'a']]

    @classmethod
    def current(cls) -> ta.Optional['_MaysyncContext']:
        return _MaysyncThreadLocal.context

    @abc.abstractmethod
    def run(self, fn: ta.Callable[..., T], *args: ta.Any, **kwargs: ta.Any) -> T:
        raise NotImplementedError


@ta.final
class _SyncMaysyncContext(_MaysyncContext):
    mode: ta.ClassVar[ta.Literal['s']] = 's'

    def run(self, fn: ta.Callable[..., T], *args: ta.Any, **kwargs: ta.Any) -> T:
        prev = _MaysyncThreadLocal.context
        _MaysyncThreadLocal.context = self

        ph = sys.get_asyncgen_hooks()
        sys.set_asyncgen_hooks(firstiter=None, finalizer=None)

        try:
            return fn(*args, **kwargs)

        finally:
            sys.set_asyncgen_hooks(*ph)

            _MaysyncThreadLocal.context = prev


@ta.final
class _AsyncMaysyncContext(_MaysyncContext):
    mode: ta.ClassVar[ta.Literal['a']] = 'a'

    def run(self, fn: ta.Callable[..., T], *args: ta.Any, **kwargs: ta.Any) -> T:
        prev = _MaysyncThreadLocal.context
        _MaysyncThreadLocal.context = self

        try:
            return fn(*args, **kwargs)

        finally:
            _MaysyncThreadLocal.context = prev


##


class _MaywaitableLike(
    abc.ABC,
    ta.Generic[_MaysyncX],
):
    """Abstract base class for the maysync versions of `Awaitable[T]` and `AsyncGenerator[O, I]`."""

    @ta.final
    def __init__(
            self,
            x: _MaysyncX,
            args: ta.Tuple[ta.Any, ...],
            kwargs: ta.Mapping[str, ta.Any],
    ) -> None:
        self._x = x
        self._args = args
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._x!r})'


class _Maywaitable(
    _MaywaitableLike[_MaysyncX],
    abc.ABC,
    ta.Generic[_MaysyncX, T],
):
    pass


class _MaysyncGenerator(
    _MaywaitableLike[_MaysyncX],
    abc.ABC,
    ta.Generic[_MaysyncX, O, I],
):
    pass


##


class _FpMaysyncFnLike(
    abc.ABC,
    ta.Generic[_MaysyncRS, _MaysyncRA],
):
    """A maysync object backed by an underlying (sync, async) function pair."""

    def __init__(
            self,
            s: ta.Callable[..., _MaysyncRS],
            a: ta.Callable[..., _MaysyncRA],
    ) -> None:
        if s is None:
            raise TypeError(s)
        if a is None:
            raise TypeError(a)
        self._s = s
        self._a = a

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._s!r}, {self._a!r})'

    def fn_pair(self) -> ta.Optional[Maysync_.FnPair]:
        return Maysync_.FnPair(
            self._s,
            self._a,
        )

    def __get__(self, instance, owner=None):
        return self.__class__(
            self._s.__get__(instance, owner),  # noqa
            self._a.__get__(instance, owner),  # noqa
        )


@ta.final
class _FpMaysyncFn(
    _FpMaysyncFnLike[T, ta.Awaitable[T]],
    MaysyncFn_[T],
    ta.Generic[T],
):
    def __call__(self, *args, **kwargs):
        return _FpMaywaitable(self, args, kwargs)


@ta.final
class _FpMaywaitable(
    _Maywaitable[_FpMaysyncFn[T], T],
):
    def s(self) -> T:
        return self._x._s(*self._args, **self._kwargs)  # noqa

    def a(self) -> ta.Awaitable[T]:
        if _MaysyncContext.current() is not None:
            return _MaysyncFuture(self._x, self._args, self._kwargs)

        return self._x._a(*self._args, **self._kwargs)  # noqa


def make_maysync_fn(
        s: ta.Callable[..., T],
        a: ta.Callable[..., ta.Awaitable[T]],
) -> MaysyncFn[T]:
    """Constructs a MaysyncFn from a (sync, async) function pair."""

    return _FpMaysyncFn(s, a)


@ta.final
class _FpMaysyncGeneratorFn(
    _FpMaysyncFnLike[ta.Generator[O, I, None], ta.AsyncGenerator[O, I]],
    MaysyncGeneratorFn_[O, I],
    ta.Generic[O, I],
):
    def __call__(self, *args, **kwargs):
        return _FpMaysyncGenerator(self, args, kwargs)


@ta.final
class _FpMaysyncGenerator(
    _MaysyncGenerator[_FpMaysyncGeneratorFn[O, I], O, I],
):
    def s(self) -> ta.Generator[O, I, None]:
        return self._x._s(*self._args, **self._kwargs)  # noqa

    def a(self) -> ta.AsyncGenerator[O, I]:
        if (ctx := _MaysyncContext.current()) is not None and ctx.mode == 's':
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

        return self._x._a(*self._args, **self._kwargs)  # noqa


def make_maysync_generator_fn(
        s: ta.Callable[..., ta.Generator[O, I, None]],
        a: ta.Callable[..., ta.AsyncGenerator[O, I]],
) -> MaysyncGeneratorFn[O, I]:
    """Constructs a MaysyncGeneratorFn from a (sync, async) generator function pair."""

    return _FpMaysyncGeneratorFn(s, a)


@ta.overload
def make_maysync(
        s: ta.Callable[..., T],
        a: ta.Callable[..., ta.Awaitable[T]],
) -> MaysyncFn[T]:
    ...


@ta.overload
def make_maysync(
        s: ta.Callable[..., ta.Generator[O, I, None]],
        a: ta.Callable[..., ta.AsyncGenerator[O, I]],
) -> MaysyncGeneratorFn[O, I]:
    ...


def make_maysync(s, a):
    """
    Constructs a MaysyncFn or MaysyncGeneratorFn from a (sync, async) function pair, using `inspect.isasyncgenfunction`
    to determine the type.
    """

    if inspect.isasyncgenfunction(a):
        return make_maysync_generator_fn(s, a)
    else:
        return make_maysync_fn(s, a)


##


class _MgMaysyncFnLike(
    abc.ABC,
    ta.Generic[T],
):
    def __init__(
            self,
            mg: ta.Callable[..., T],
    ) -> None:
        self._mg = mg

        functools.update_wrapper(self, mg, updated=())

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._mg!r})'

    def fn_pair(self) -> ta.Optional[Maysync_.FnPair]:
        return None

    def __get__(self, instance, owner=None):
        return self.__class__(
            self._mg.__get__(instance, owner),  # noqa
        )

    @abc.abstractmethod  # noqa
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


@ta.final
class _MgMaysyncFn(
    _MgMaysyncFnLike[ta.Awaitable[T]],
    MaysyncFn_[T],
    ta.Generic[T],
):
    def __call__(self, *args, **kwargs):
        return _MgMaywaitable(self, args, kwargs)


@ta.final
class _MgMaysyncDriver:
    def __init__(self, ctx, mg):
        self.ctx = ctx
        self.mg = mg

    value: ta.Any

    def __iter__(self):
        try:
            a = self.mg.__await__()
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
                    self.ctx.run(g.close)

            finally:
                self.ctx.run(a.close)

        finally:
            self.ctx.run(self.mg.close)


@ta.final
class _MgMaywaitable(
    _Maywaitable[_MgMaysyncFn[T], T],
):
    def _driver(self, ctx: _MaysyncContext) -> _MgMaysyncDriver:
        return _MgMaysyncDriver(ctx, self._x._mg(*self._args, **self._kwargs))  # noqa

    def s(self) -> T:
        for f in (drv := self._driver(_SyncMaysyncContext())):
            f.s()
            del f

        return drv.value

    def a(self) -> ta.Awaitable[T]:
        if (ctx := _MaysyncContext.current()) is None or ctx.mode == 'a':
            return self._x._mg(*self._args, **self._kwargs)  # noqa

        async def inner():
            for f in (drv := self._driver(_AsyncMaysyncContext())):
                await f.a()
                del f

            return drv.value

        return inner()


@ta.final
class _MgMaysyncGeneratorFn(
    _MgMaysyncFnLike[ta.AsyncGenerator[O, I]],
    MaysyncGeneratorFn_[O, I],
    ta.Generic[O, I],
):
    def __call__(self, *args, **kwargs):
        return _MgMaysyncGenerator(self, args, kwargs)


@ta.final
class _MgMaysyncGeneratorDriver:
    def __init__(self, ctx, ag):
        self.ctx = ctx
        self.ag = ag

    def __iter__(self):
        try:
            ai = self.ag.__aiter__()
            try:
                i: ta.Any = None
                e: ta.Any = None

                while True:
                    if e is not None:
                        coro = ai.athrow(e)
                    else:
                        coro = ai.asend(i)

                    i = None
                    e = None

                    for f in (drv := _MgMaysyncDriver(self.ctx, coro)):
                        if (x := (yield ('f', f))) is not None:
                            raise RuntimeError(x)

                        del f

                    i, e = yield ('o', drv.value)

            finally:
                for f in _MgMaysyncDriver(self.ctx, ai.aclose()):
                    yield ('f', f)

        finally:
            for f in _MgMaysyncDriver(self.ctx, self.ag.aclose()):
                yield ('f', f)


@ta.final
class _MgMaysyncGenerator(
    _MaysyncGenerator[_MgMaysyncGeneratorFn[O, I], O, I],
):
    def _driver(self, ctx: _MaysyncContext) -> _MgMaysyncGeneratorDriver:
        return _MgMaysyncGeneratorDriver(ctx, self._x._mg(*self._args, **self._kwargs))  # noqa

    def s(self) -> ta.Generator[O, I, None]:
        di = iter(self._driver(_SyncMaysyncContext()))

        ie: ta.Any = None

        while True:
            try:
                t, x = di.send(ie)
            except StopAsyncIteration:
                return
            except StopIteration:
                raise RuntimeError from None

            ie = None

            if t == 'f':
                x.s()

            elif t == 'o':
                try:
                    ie = ((yield x), None)
                except BaseException as ex:  # noqa
                    ie = (None, ex)

            else:
                raise RuntimeError((t, x))

            del x

    def a(self) -> ta.AsyncGenerator[O, I]:
        if _MaysyncContext.current() is not None:
            return self._x._mg(*self._args, **self._kwargs)  # noqa

        async def inner():
            di = iter(self._driver(_AsyncMaysyncContext()))

            ie: ta.Any = None

            while True:
                try:
                    t, x = di.send(ie)
                except StopAsyncIteration:
                    return
                except StopIteration:
                    raise RuntimeError from None

                ie = None

                if t == 'f':
                    await x.a()

                elif t == 'o':
                    try:
                        ie = ((yield x), None)
                    except BaseException as ex:  # noqa
                        ie = (None, ex)

                else:
                    raise RuntimeError((t, x))

                del x

        return inner()


def maysync_fn(
        m: ta.Callable[..., ta.Awaitable[T]],
) -> MaysyncFn[T]:
    """Constructs a MaysyncFn from a 'maysync flavored' async function."""

    return _MgMaysyncFn(m)


def maysync_generator_fn(
        m: ta.Callable[..., ta.AsyncGenerator[O, I]],
) -> MaysyncGeneratorFn[O, I]:
    """Constructs a MaysyncGeneratorFn from a 'maysync flavored' async generator function."""

    return _MgMaysyncGeneratorFn(m)


@ta.overload
def maysync(
        m: ta.Callable[..., ta.Awaitable[T]],
) -> MaysyncFn[T]:
    ...


@ta.overload
def maysync(
        m: ta.Callable[..., ta.AsyncGenerator[O, I]],
) -> MaysyncGeneratorFn[O, I]:
    ...


def maysync(m):
    """
    Constructs a MaysyncFn or MaysyncGeneratorFn from 'maysync flavored' async function or async generator function,
    using `inspect.isasyncgenfunction` to determine the type. Usable as a decorator.
    """

    if inspect.isasyncgenfunction(m):
        return maysync_generator_fn(m)
    else:
        return maysync_fn(m)


##


@ta.final
class _MaysyncFutureNotAwaitedError(RuntimeError):
    pass


@ta.final
class _MaysyncFuture(ta.Generic[T]):
    def __init__(
            self,
            x: ta.Any,
            args: ta.Tuple[ta.Any, ...],
            kwargs: ta.Mapping[str, ta.Any],
    ) -> None:
        self.x = x
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self.x!r}, done={self.done!r})'

    done: bool = False
    result: T
    error: ta.Optional[BaseException] = None

    def __await__(self):
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
            self.result = self.x(*self.args, **self.kwargs).s()
        except BaseException as ex:  # noqa
            self.error = ex
        self.done = True

    async def a(self) -> None:
        if self.done:
            return

        try:
            self.result = await self.x(*self.args, **self.kwargs).a()
        except BaseException as ex:  # noqa
            self.error = ex
        self.done = True
