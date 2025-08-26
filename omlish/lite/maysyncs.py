# ruff: noqa: UP006 UP043 UP045
# @omlish-lite
"""
A system for writing a python function once which can then be effectively used in both sync and async contexts -
including IO, under any (or no) event loop.

Where an 'async fn' returns an 'awaitable', a 'maysync fn' returns a 'maywaitable', which is an object with three
nullary methods:

 - `def s()` - to be called in sync contexts
 - `async def a()` - to be called in async contexts
 - `async def m()` - to be called in maysync contexts

For example, a maysync function `m_inc_int(x: int) -> int` would be used as such:

 - `assert m_inc_int(5).s() == 6` in sync contexts
 - `assert await m_inc_int(5).a() == 6` in async contexts
 - `assert await m_inc_int(5).m() == 6` in maysync contexts

Maysync fns may be constructed in two ways: either using `make_maysync`, providing an equivalent pair of sync and async
functions, or using the `@maysync` decorator to wrap a 'maysync flavored' async function. 'Maysync flavored' async
functions are ones which only call other maysync functions through their 'maysync context' - that is, they (and they
alone) use the 'm' methods on maywaitables - for example: `await m_foo().m()`. Being regular python functions they are
free to call whatever they like - for example doing sync IO - but the point is to, ideally, route all IO through maysync
functions such that the maysync code is fully efficiently usable in any context.

This code is still written in a very dumb and explicit style primarily for auditability, but secondarily to minimize
performance impact.

Internally, it's not really correct to say that there is 'no event loop' in the maysync context - rather, each call to
a maysync fn runs within its own tiny event loop.

===

TODO:
 - __del__
 - (test) maysync context managers
 - CancelledError
 - sys.set_asyncgen_hooks probably
 - is _MaysyncGeneratorYield awaitable?
 - for debug, mask any running eventloop while running maysync code
 - `[CO_ASYNC_GENERATOR] = {k for k, v in dis.COMPILER_FLAG_NAMES.items() if v == 'ASYNC_GENERATOR'}` ? inspect is big..
  - works down to 3.8
 - if we already have to touch a threadlocal via asyncgen_hooks, should we just go ahead and make `a()` *auto*? :/
  - would this straight up remove half the code and speed up the async path to native speed?
"""
import abc
import functools
import inspect
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
     - `async def a()` - to be called in async contexts
     - `async def m()` - to be called in maysync contexts

    Only the proper method should be called in each context.
    """

    def s(self) -> T_co:
        ...

    def a(self) -> ta.Awaitable[T_co]:
        ...

    def m(self) -> ta.Awaitable[T_co]:
        ...


class MaysyncGenerator(ta.Protocol[O_co, I_contra]):
    """
    The maysync version of `AsyncGenerator[O, I]`. Generator maysync functions return a `MaysyncGenerator`, with the
    following methods:

     - `def s()` - to be called in sync contexts
     - `async def a()` - to be called in async contexts
     - `async def m()` - to be called in maysync contexts

    Only the proper method should be called in each context.
    """

    def s(self) -> ta.Generator[O_co, I_contra, None]:
        ...

    def a(self) -> ta.AsyncGenerator[O_co, I_contra]:
        ...

    def m(self) -> ta.AsyncGenerator[O_co, I_contra]:
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
    @ta.final
    def m(self) -> ta.Awaitable[T]:
        return _MaysyncFuture(_MaysyncOp(
            self._x,
            self._args,
            self._kwargs,
        ))


class _MaysyncGenerator(
    _MaywaitableLike[_MaysyncX],
    abc.ABC,
    ta.Generic[_MaysyncX, O, I],
):
    @ta.final
    def m(self) -> ta.AsyncGenerator[O, I]:
        return _MaysyncRunningGenerator(_MaysyncOp(  # noqa
            self._x,
            self._args,
            self._kwargs,
        ))


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

    async def a(self) -> T:
        return await self._x._a(*self._args, **self._kwargs)  # noqa


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
        yield from self._x._s(*self._args, **self._kwargs)  # noqa

    async def a(self) -> ta.AsyncGenerator[O, I]:
        g = self._x._a(*self._args, **self._kwargs)  # noqa

        i: ta.Any = None
        e: ta.Any = None

        try:
            while True:
                try:
                    if e is not None:
                        o = await g.athrow(e)
                    else:
                        o = await g.asend(i)
                except StopAsyncIteration:
                    return

                i = None
                e = None

                try:
                    i = yield o
                except BaseException as ex:  # noqa
                    e = ex

                del o

        finally:
            await g.aclose()


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
    """
    A maysync object backed by an underlying generator yielding _MaysyncOp's. The _MgDriver and _MgGeneratorDriver
    classes produce such generators.
    """

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


class _MgMaysyncFn(
    _MgMaysyncFnLike[ta.Generator[ta.Union['_MaysyncOp', '_MaysyncGeneratorOp'], ta.Any, T]],
    MaysyncFn_[T],
    ta.Generic[T],
):
    def __call__(self, *args, **kwargs):
        return _MgMaywaitable(self, args, kwargs)


@ta.final
class _MgMaywaitable(_Maywaitable[_MgMaysyncFn[T], T]):
    def s(self) -> T:
        g = self._x._mg(*self._args, **self._kwargs)  # noqa
        try:
            i: ta.Any = None
            e: ta.Any = None

            while True:
                try:
                    if e is not None:
                        o = g.throw(e)
                    else:
                        o = g.send(i)
                except StopIteration as ex:
                    return ex.value

                i = None
                e = None

                if isinstance(o, _MaysyncOp):
                    try:
                        i = o.x(*o.args, **o.kwargs).s()
                    except BaseException as ex:  # noqa
                        e = ex

                elif isinstance(o, _MaysyncGeneratorOp):
                    # FIXME: finally: .close
                    try:
                        ug = o.rg.ug
                    except AttributeError:
                        ug = o.rg.ug = o.rg.op.x(*o.rg.op.args, **o.rg.op.kwargs).s()

                    if o.c == 'send':
                        gl = lambda: ug.send(*o.args)  # noqa
                    elif o.c == 'throw':
                        gl = lambda: ug.throw(*o.args)  # noqa
                    elif o.c == 'close':
                        raise NotImplementedError
                    else:
                        raise RuntimeError(o.c)

                    try:
                        i = gl()
                    except StopIteration as ex:
                        if ex.value is not None:
                            raise TypeError from ex
                        e = StopAsyncIteration
                    except BaseException as ex:  # noqa
                        e = ex

                else:
                    raise TypeError(o)

                del o

        finally:
            g.close()

    async def a(self) -> T:
        g = self._x._mg(*self._args, **self._kwargs)  # noqa
        try:
            i: ta.Any = None
            e: ta.Any = None

            while True:
                try:
                    if e is not None:
                        o = g.throw(e)
                    else:
                        o = g.send(i)
                except StopIteration as ex:
                    return ex.value

                i = None
                e = None

                if isinstance(o, _MaysyncOp):
                    try:
                        i = await o.x(*o.args, **o.kwargs).a()
                    except BaseException as ex:  # noqa
                        e = ex

                elif isinstance(o, _MaysyncGeneratorOp):
                    # FIXME: finally: .close
                    try:
                        ug = o.rg.ug
                    except AttributeError:
                        ug = o.rg.ug = o.rg.op.x(*o.rg.op.args, **o.rg.op.kwargs).a().__aiter__()

                    if o.c == 'send':
                        gl = lambda: ug.asend(*o.args)  # noqa
                    elif o.c == 'throw':
                        gl = lambda: ug.athrow(*o.args)  # noqa
                    elif o.c == 'close':
                        raise NotImplementedError
                    else:
                        raise RuntimeError(o.c)

                    try:
                        i = await gl()
                    except BaseException as ex:  # noqa
                        e = ex

                else:
                    raise TypeError(o)

                del o

        finally:
            g.close()


class _MgMaysyncGeneratorFn(
    _MgMaysyncFnLike[ta.Any],  # ?? #ta.Generator[ta.Union['_MaysyncOp', '_MaysyncGeneratorOp'], ta.Any, T]],
    MaysyncGeneratorFn_[O, I],
    ta.Generic[O, I],
):
    def __call__(self, *args, **kwargs):
        return _MgMaysyncGenerator(self, args, kwargs)


@ta.final
class _MgMaysyncGenerator(
    _MaysyncGenerator[_MgMaysyncGeneratorFn[O, I], O, I],
):
    def s(self) -> ta.Generator[O, I, None]:
        g = self._x._mg(*self._args, **self._kwargs)  # noqa
        try:
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
                        raise TypeError from ex
                    return

                i = None
                e = None

                if isinstance(o, _MaysyncGeneratorYield):
                    try:
                        i = yield o.v
                    except BaseException as ex:  # noqa
                        e = ex

                elif isinstance(o, _MaysyncOp):
                    try:
                        i = o.x(*o.args, **o.kwargs).s()
                    except BaseException as ex:  # noqa
                        e = ex

                elif isinstance(o, _MaysyncGeneratorOp):
                    # FIXME: finally: .close
                    try:
                        ug = o.rg.ug
                    except AttributeError:
                        ug = o.rg.ug = o.rg.op.x(*o.rg.op.args, **o.rg.op.kwargs).s()

                    if o.c == 'send':
                        gl = lambda: ug.send(*o.args)  # noqa
                    elif o.c == 'throw':
                        gl = lambda: ug.throw(*o.args)  # noqa
                    elif o.c == 'close':
                        raise NotImplementedError
                    else:
                        raise RuntimeError(o.c)

                    try:
                        i = gl()
                    except StopIteration as ex:
                        if ex.value is not None:
                            raise TypeError from ex
                        e = StopAsyncIteration
                    except BaseException as ex:  # noqa
                        e = ex

                else:
                    raise TypeError(o)

                del o

        finally:
            g.close()

    async def a(self) -> ta.AsyncGenerator[O, I]:
        g = self._x._mg(*self._args, **self._kwargs)  # noqa
        try:
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
                        raise TypeError from ex
                    return

                i = None
                e = None

                if isinstance(o, _MaysyncGeneratorYield):
                    try:
                        i = yield o.v
                    except BaseException as ex:  # noqa
                        e = ex

                elif isinstance(o, _MaysyncOp):
                    try:
                        i = await o.x(*o.args, **o.kwargs).a()
                    except BaseException as ex:  # noqa
                        e = ex

                elif isinstance(o, _MaysyncGeneratorOp):
                    # FIXME: finally: .close
                    try:
                        ug = o.rg.ug
                    except AttributeError:
                        ug = o.rg.ug = o.rg.op.x(*o.rg.op.args, **o.rg.op.kwargs).a().__aiter__()

                    if o.c == 'send':
                        gl = lambda: ug.asend(*o.args)  # noqa
                    elif o.c == 'throw':
                        gl = lambda: ug.athrow(*o.args)  # noqa
                    elif o.c == 'close':
                        raise NotImplementedError
                    else:
                        raise RuntimeError(o.c)

                    try:
                        i = await gl()
                    except StopIteration as ex:
                        if ex.value is not None:
                            raise TypeError from ex
                        e = StopAsyncIteration
                    except BaseException as ex:  # noqa
                        e = ex

                else:
                    raise TypeError(o)

                del o

        finally:
            g.close()


#


class _MgDriverLike(abc.ABC):
    """
    Abstract base class for the _MgDriver and _MgGeneratorDriver classes, which produce generators yielding _MaysyncOp's
    from a given underlying 'masync flavored' async function provided by the user.
    """

    def __init__(self, m):
        self._m = m

        functools.update_wrapper(self, m, updated=())

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._m!r})'

    def __get__(self, instance, owner=None):
        return self.__class__(
            self._m.__get__(instance, owner),
        )

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


@ta.final
class _MgDriver(_MgDriverLike):
    def __call__(self, *args, **kwargs):
        a_ = self._m(*args, **kwargs)
        try:
            a = a_.__await__()
            try:
                g = iter(a)
                try:
                    while True:
                        try:
                            o = g.send(None)
                        except StopIteration as e:
                            return e.value

                        if isinstance(o, _MaysyncFuture):
                            if not o.done:
                                try:
                                    o.result = yield o.op
                                except BaseException as e:  # noqa
                                    o.error = e
                                o.done = True

                        else:
                            raise TypeError(o)

                        del o

                finally:
                    g.close()

            finally:
                a.close()

        finally:
            a_.close()


def maysync_fn(
        m: ta.Callable[..., ta.Awaitable[T]],
) -> MaysyncFn[T]:
    """Constructs a MaysyncFn from a 'maysync flavored' async function."""

    return _MgMaysyncFn(_MgDriver(m))


@ta.final
class _MgGeneratorDriver(_MgDriverLike):
    def __call__(self, *args, **kwargs):
        ag = self._m(*args, **kwargs)
        ai = ag.__aiter__()

        i: ta.Any = None
        e: ta.Any = None

        while True:
            if e is not None:
                coro = ai.athrow(e)
            else:
                coro = ai.asend(i)

            i = None
            e = None

            try:
                g = coro.__await__()
                while True:
                    try:
                        o = g.send(None)
                    except StopIteration as ex:
                        i = ex.value
                        break
                    except StopAsyncIteration:
                        # FIXME: aclose
                        return
                    except BaseException as ex:  # noqa
                        e = ex
                        break

                    if isinstance(o, _MaysyncFuture):
                        if not o.done:
                            try:
                                o.result = yield o.op
                            except BaseException as ex:  # noqa
                                o.error = ex
                            o.done = True

                    else:
                        raise TypeError(o)

            finally:
                coro.close()

            try:
                i = yield _MaysyncGeneratorYield(i)
            except BaseException as ex:  # noqa
                e = ex


def maysync_generator_fn(
        m: ta.Callable[..., ta.AsyncGenerator[O, I]],
) -> MaysyncGeneratorFn[O, I]:
    """Constructs a MaysyncGeneratorFn from a 'maysync flavored' async generator function."""

    return _MgMaysyncGeneratorFn(_MgGeneratorDriver(m))


@ta.overload
def maysync(m: ta.Callable[..., ta.Awaitable[T]]) -> MaysyncFn[T]:
    ...


@ta.overload
def maysync(m: ta.Callable[..., ta.AsyncGenerator[O, I]]) -> MaysyncGeneratorFn[O, I]:
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


class _MaysyncFutureNotAwaitedError(RuntimeError):
    pass


@ta.final
class _MaysyncFuture(ta.Generic[T]):
    def __init__(
            self,
            op: ta.Union['_MaysyncOp', '_MaysyncGeneratorOp'],
    ) -> None:
        self.op = op

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self.op!r}, done={self.done!r})'

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


@ta.final
class _MaysyncOp:
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
        return f'{self.__class__.__name__}@{id(self):x}({self.x!r})'


@ta.final
class _MaysyncGeneratorYield(ta.NamedTuple):
    v: ta.Any


@ta.final
class _MaysyncGeneratorOp:
    def __init__(
            self,
            rg: '_MaysyncRunningGenerator',
            c: ta.Literal['send', 'throw', 'close'],
            args: ta.Tuple[ta.Any, ...],
    ) -> None:
        self.rg = rg
        self.c = c
        self.args = args

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self.rg!r}, {self.c!r})'


@ta.final
class _MaysyncRunningGenerator:
    def __init__(
            self,
            op: _MaysyncOp,
    ) -> None:
        self.op = op

    ug: ta.Any

    def __aiter__(self):
        return self

    def __anext__(self):
        return self.asend(None)

    def asend(self, value):
        return _MaysyncFuture(_MaysyncGeneratorOp(self, 'send', (value,)))

    def athrow(self, et, e=None, tb=None):
        return _MaysyncFuture(_MaysyncGeneratorOp(self, 'throw', (et, e, tb)))

    def aclose(self):
        return _MaysyncFuture(_MaysyncGeneratorOp(self, 'close', ()))
