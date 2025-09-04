import typing as ta

from ..lite.maysync import MaysyncFn
from ..lite.maysync import MaysyncGeneratorFn
from ..lite.maysync import make_maysync as _make_maysync
from .asyncs import as_async


T = ta.TypeVar('T')
O = ta.TypeVar('O')
I = ta.TypeVar('I')

P = ta.ParamSpec('P')


##


def make_maysync_fn(
        s: ta.Callable[P, T],
        a: ta.Callable[P, ta.Awaitable[T]],
) -> ta.Callable[P, ta.Awaitable[T]]:
    """Constructs a MaysyncFn from a (sync, async) function pair."""

    return MaysyncFn(s, a)


def make_maysync_generator_fn(
        s: ta.Callable[P, ta.Generator[O, I]],
        a: ta.Callable[P, ta.AsyncGenerator[O, I]],
) -> ta.Callable[P, ta.AsyncGenerator[O, I]]:
    """Constructs a MaysyncGeneratorFn from a (sync, async) generator function pair."""

    return MaysyncGeneratorFn(s, a)


@ta.overload
def make_maysync(
        s: ta.Callable[P, T],
        a: ta.Callable[P, ta.Awaitable[T]],
) -> ta.Callable[P, ta.Awaitable[T]]:
    ...


@ta.overload
def make_maysync(
        s: ta.Callable[P, ta.Generator[O, I]],
        a: ta.Callable[P, ta.AsyncGenerator[O, I]],
) -> ta.Callable[P, ta.AsyncGenerator[O, I]]:
    ...


def make_maysync(s, a):
    """
    Constructs a MaysyncFn or MaysyncGeneratorFn from a (sync, async) function pair, using `inspect.isasyncgenfunction`
    to determine the type.
    """

    return _make_maysync(s, a)


##


def make_maysync_from_sync(
        s: ta.Callable[P, T],
        a: ta.Callable[P, ta.Awaitable[T]] | None = None,
) -> ta.Callable[P, ta.Awaitable[T]]:
    return _make_maysync(
        s,
        a if a is not None else as_async(s, wrap=True),
    )
