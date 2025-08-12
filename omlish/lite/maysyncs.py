# ruff: noqa: UP045
# @omlish-lite
"""
TODO:
 - __del__
"""
import abc
import functools
import typing as ta


T = ta.TypeVar('T')
T_co = ta.TypeVar('T_co', covariant=True)
_X = ta.TypeVar('_X')

_MaysyncGen = ta.Generator['_MaysyncOp', ta.Any, T]  # ta.TypeAlias


##


class Maywaitable(ta.Protocol[T_co]):
    def s(self) -> T_co:
        ...

    def a(self) -> ta.Awaitable[T_co]:
        ...

    def m(self) -> ta.Awaitable[T_co]:
        ...


Maysync = ta.Callable[..., Maywaitable[T]]  # ta.TypeAlias  # omlish-amalg-typing-no-move


class Maysync_(abc.ABC):  # noqa
    pass


##


class _Maywaitable(abc.ABC, ta.Generic[_X, T]):
    @ta.final
    def __init__(
            self,
            x: _X,
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        self.x = x
        self.args = args
        self.kwargs = kwargs

    @ta.final
    def m(self) -> ta.Awaitable[T]:
        return _MaysyncFuture(_MaysyncOp(
            ta.cast(ta.Any, self.x),
            *self.args,
            **self.kwargs,
        ))


##


@ta.final
class _FnMaysync(Maysync_, ta.Generic[T]):
    def __init__(
            self,
            s: ta.Callable[..., T],
            a: ta.Callable[..., ta.Awaitable[T]],
    ) -> None:
        if s is None:
            raise TypeError(s)
        if a is None:
            raise TypeError(a)
        self.s = s
        self.a = a

    def __get__(self, instance, owner=None):
        return _FnMaysync(
            self.s.__get__(instance, owner),  # noqa
            self.a.__get__(instance, owner),  # noqa
        )

    def __call__(self, *args, **kwargs):
        return _FnMaywaitable(self, *args, **kwargs)


@ta.final
class _FnMaywaitable(_Maywaitable[_FnMaysync[T], T]):
    def s(self) -> T:
        return self.x.s(*self.args, **self.kwargs)

    async def a(self) -> T:
        return await self.x.a(*self.args, **self.kwargs)


def make_maysync(
        s: ta.Callable[..., T],
        a: ta.Callable[..., ta.Awaitable[T]],
) -> Maysync[T]:
    return _FnMaysync(s, a)


##


@ta.final
class _MgMaysync(Maysync_, ta.Generic[T]):
    def __init__(
            self,
            mg: ta.Callable[..., _MaysyncGen[T]],
    ) -> None:
        self.mg = mg

    def __get__(self, instance, owner=None):
        return _MgMaysync(
            self.mg.__get__(instance, owner),  # noqa
        )

    def __call__(self, *args, **kwargs):
        return _MgMaywaitable(self, *args, **kwargs)


@ta.final
class _MgMaywaitable(_Maywaitable[_MgMaysync[T], T]):
    def s(self) -> T:
        g = self.x.mg(*self.args, **self.kwargs)

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

            if not isinstance(o, _MaysyncOp):
                raise TypeError(o)

            try:
                i = o.x(*o.args, **o.kwargs).s()
            except BaseException as ex:  # noqa
                e = ex

            del o

    async def a(self) -> T:
        g = self.x.mg(*self.args, **self.kwargs)

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

            if not isinstance(o, _MaysyncOp):
                raise TypeError(o)

            try:
                i = await o.x(*o.args, **o.kwargs).a()
            except BaseException as ex:  # noqa
                e = ex

            del o


@ta.final
class _MgMaysyncFn:
    def __init__(self, m):
        self.m = m

        functools.update_wrapper(self, m)

    def __get__(self, instance, owner=None):
        return _MgMaysyncFn(
            self.m.__get__(instance, owner),
        )

    def __call__(self, *args, **kwargs):
        a = self.m(*args, **kwargs).__await__()
        try:
            g = iter(a)
            try:
                while True:
                    try:
                        o = g.send(None)
                    except StopIteration as e:
                        return e.value

                    if not isinstance(o, _MaysyncFuture):
                        raise TypeError(o)

                    if not o.done:
                        try:
                            o.result = yield o.op
                        except BaseException as e:  # noqa
                            o.error = e
                        o.done = True

                    del o

            finally:
                g.close()

        finally:
            a.close()


def maysync(m: ta.Callable[..., ta.Awaitable[T]]) -> Maysync[T]:
    return _MgMaysync(_MgMaysyncFn(m))


##


@ta.final
class _MaysyncOp:
    def __init__(
            self,
            x: Maysync[T],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        self.x = x
        self.args = args
        self.kwargs = kwargs


class _MaysyncFutureNotAwaitedError(RuntimeError):
    pass


@ta.final
class _MaysyncFuture(ta.Generic[T]):
    def __init__(
            self,
            op: _MaysyncOp,
    ) -> None:
        self.op = op

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
