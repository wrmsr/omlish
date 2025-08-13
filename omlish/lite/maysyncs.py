# ruff: noqa: UP006 UP045
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

_MaysyncX = ta.TypeVar('_MaysyncX')

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


class Maysync_(abc.ABC, ta.Generic[T]):  # noqa
    @ta.final
    def cast(self) -> Maysync[T]:
        return ta.cast('Maysync[T]', self)

    class FnPair(ta.NamedTuple):
        s: ta.Callable[..., ta.Any]
        a: ta.Callable[..., ta.Awaitable[ta.Any]]

    @abc.abstractmethod
    def fn_pair(self) -> ta.Optional[FnPair]:
        raise NotImplementedError

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):  # -> Maywaitable[T]
        raise NotImplementedError


##


class _Maywaitable(abc.ABC, ta.Generic[_MaysyncX, T]):
    @ta.final
    def __init__(
            self,
            x: _MaysyncX,
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        self._x = x
        self._args = args
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._x!r})'

    @ta.final
    def m(self) -> ta.Awaitable[T]:
        return _MaysyncFuture(_MaysyncOp(
            ta.cast(ta.Any, self._x),
            self._args,
            self._kwargs,
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
        return _FnMaysync(
            self._s.__get__(instance, owner),  # noqa
            self._a.__get__(instance, owner),  # noqa
        )

    def __call__(self, *args, **kwargs):
        return _FnMaywaitable(self, *args, **kwargs)


@ta.final
class _FnMaywaitable(_Maywaitable[_FnMaysync[T], T]):
    def s(self) -> T:
        return self._x._s(*self._args, **self._kwargs)  # noqa

    async def a(self) -> T:
        return await self._x._a(*self._args, **self._kwargs)  # noqa


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
        self._mg = mg

        functools.update_wrapper(self, mg, updated=())

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._mg!r})'

    def fn_pair(self) -> ta.Optional[Maysync_.FnPair]:
        return None

    def __get__(self, instance, owner=None):
        return _MgMaysync(
            self._mg.__get__(instance, owner),  # noqa
        )

    def __call__(self, *args, **kwargs):
        return _MgMaywaitable(self, *args, **kwargs)


@ta.final
class _MgMaywaitable(_Maywaitable[_MgMaysync[T], T]):
    def s(self) -> T:
        g = self._x._mg(*self._args, **self._kwargs)  # noqa

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
        g = self._x._mg(*self._args, **self._kwargs)  # noqa

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
        self._m = m

        functools.update_wrapper(self, m, updated=())

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._m!r})'

    def __get__(self, instance, owner=None):
        return _MgMaysyncFn(
            self._m.__get__(instance, owner),
        )

    def __call__(self, *args, **kwargs):
        a = self._m(*args, **kwargs).__await__()
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
            args: ta.Tuple[ta.Any, ...],
            kwargs: ta.Mapping[str, ta.Any],
    ) -> None:
        self.x = x
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self.x!r})'


class _MaysyncFutureNotAwaitedError(RuntimeError):
    pass


@ta.final
class _MaysyncFuture(ta.Generic[T]):
    def __init__(
            self,
            op: _MaysyncOp,
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
