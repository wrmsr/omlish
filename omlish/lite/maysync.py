# ruff: noqa: UP045
import abc
import dataclasses as dc
import typing as ta

from .args import Args


T = ta.TypeVar('T')


MaysyncGen = ta.Generator['MaysyncOp', ta.Any, T]  # ta.TypeAlias
MaysyncFn = ta.Callable[..., MaysyncGen[T]]  # ta.TypeAlias


##


@dc.dataclass(frozen=True)
class MaysyncOp(ta.Generic[T]):
    fn: ta.Callable[..., T]
    a_fn: ta.Callable[..., ta.Awaitable[T]]

    args: ta.Optional[Args] = None

    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> 'MaysyncOp[T]':
        if self.args is not None:
            raise RuntimeError('Args already bound')
        return dc.replace(self, args=Args(*args, **kwargs))


maysync_op = MaysyncOp


##


def maysync(fn: MaysyncFn[T], *args: ta.Any, **kwargs: ta.Any) -> T:
    g = fn(*args, **kwargs)
    i = None
    while True:
        try:
            o = g.send(i)
        except StopIteration as e:
            return e.value
        i = Args.call(o.fn, o.args)


async def a_maysync(fn: MaysyncFn[T], *args: ta.Any, **kwargs: ta.Any) -> T:
    g = fn(*args, **kwargs)
    i = None
    while True:
        try:
            o = g.send(i)
        except StopIteration as e:
            return e.value
        i = await Args.call(o.a_fn, o.args)


##


class MaysyncRunnable(abc.ABC, ta.Generic[T]):
    @abc.abstractmethod
    def m_run(self) -> MaysyncGen[T]:
        raise NotImplementedError

    @ta.final
    def run(self) -> T:
        return maysync(self.m_run)

    @ta.final
    async def a_run(self) -> T:
        return await a_maysync(self.m_run)
