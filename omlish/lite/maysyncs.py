# ruff: noqa: UP045
# @omlish-lite
import abc
import dataclasses as dc
import functools
import typing as ta

from .args import Args
from .check import check


T = ta.TypeVar('T')

_MaysyncGen = ta.Generator['_MaysyncOp', ta.Any, T]  # ta.TypeAlias


##


@dc.dataclass(frozen=True, eq=False)
class Maysyncable(abc.ABC, ta.Generic[T]):
    @abc.abstractmethod
    def s(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def a(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Awaitable[T]:
        raise NotImplementedError

    @ta.final
    def m(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Awaitable[T]:
        return _MaysyncFuture(_MaysyncOp(self, Args(*args, **kwargs)))


##


@dc.dataclass(frozen=True, eq=False)
class _FnMaysyncable(Maysyncable[T]):
    s: ta.Callable[..., T]
    a: ta.Callable[..., ta.Awaitable[T]]

    def __post_init__(self) -> None:
        check.not_none(self.s)
        check.not_none(self.a)

    def __init_subclass__(cls, **kwargs):
        raise TypeError


_FnMaysyncable.__abstractmethods__ = frozenset()


def make_maysync(
        s: ta.Callable[..., T],
        a: ta.Callable[..., ta.Awaitable[T]],
) -> Maysyncable[T]:
    return _FnMaysyncable(
        s,
        a,
    )


##


@dc.dataclass(frozen=True, eq=False)
class _MgMaysyncable(Maysyncable[T]):
    mg: ta.Callable[..., _MaysyncGen[T]]

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    def s(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        g = self.mg(*args, **kwargs)

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

            mo = check.isinstance(o, _MaysyncOp)
            try:
                i = mo.a(mo.mx.s)
            except BaseException as ex:  # noqa
                e = ex

    async def a(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        g = self.mg(*args, **kwargs)

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

            mo = check.isinstance(o, _MaysyncOp)
            try:
                i = await mo.a(mo.mx.a)
            except BaseException as ex:  # noqa
                e = ex


def maysync(m: ta.Callable[..., ta.Awaitable[T]]) -> Maysyncable[T]:
    @functools.wraps(m)
    def mg_fn(*args, **kwargs):
        a = m(*args, **kwargs).__await__()

        try:
            g = iter(a)
            try:
                while True:
                    try:
                        o = g.send(None)
                    except StopIteration as e:
                        return e.value

                    f = check.isinstance(o, _MaysyncFuture)
                    if not f.done:
                        try:
                            f.result = yield f.op
                        except BaseException as e:  # noqa
                            f.error = e
                        f.done = True

            finally:
                g.close()

        finally:
            a.close()

    return _MgMaysyncable(mg_fn)


##


@dc.dataclass(frozen=True, eq=False)
class _MaysyncOp:
    mx: Maysyncable
    a: Args

    def __init_subclass__(cls, **kwargs):
        raise TypeError


##


@dc.dataclass(eq=False)
class _MaysyncFuture(ta.Generic[T]):
    op: _MaysyncOp

    done: bool = False
    error: ta.Optional[BaseException] = None
    result: ta.Optional[T] = None

    def __await__(self):
        if not self.done:
            yield self
        if not self.done:
            raise RuntimeError("await wasn't used with event future")
        if self.error is not None:
            raise self.error
        return self.result
