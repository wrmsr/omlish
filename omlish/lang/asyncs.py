import functools
import typing as ta


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


def as_async(fn: ta.Callable[P, T], *, wrap: bool = False) -> ta.Callable[P, ta.Awaitable[T]]:
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)

    return functools.wraps(fn)(inner) if wrap else inner


##


async def async_list(ai: ta.AsyncIterable[T]) -> list[T]:
    """Simply eagerly reads the full contents of a function call returning an async iterator."""

    return [v async for v in ai]


##


def sync_await(aw: ta.Awaitable[T]) -> T:
    """
    Allows for the synchronous execution of async functions which will never actually *externally* await anything. These
    functions are allowed to await any number of other functions - including contextmanagers and generators - so long as
    nothing ever actually 'leaks' out of the function, presumably to an event loop.
    """

    ret = missing = object()

    async def gate():
        nonlocal ret

        ret = await aw

    cr = gate()
    try:
        try:
            cr.send(None)
        except StopIteration:
            pass

        if ret is missing or cr.cr_await is not None or cr.cr_running:
            raise TypeError('Not terminated')

    finally:
        cr.close()

    return ta.cast(T, ret)


def sync_async_list(
        ai: ta.AsyncIterable[T],
) -> list[T]:
    """
    Uses `sync_await` to synchronously read the full contents of a function call returning an async iterator, given that
    the function never externally awaits anything.
    """

    lst: list[T] | None = None

    async def inner():
        nonlocal lst

        lst = [v async for v in ai]

    sync_await(inner())

    if not isinstance(lst, list):
        raise TypeError(lst)

    return lst
