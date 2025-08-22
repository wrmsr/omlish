import typing as ta


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


async def async_list(
        fn: ta.Callable[P, ta.AsyncIterator[T]],
        *args: P.args,
        **kwargs: P.kwargs,
) -> list[T]:
    """Simply eagerly reads the full contents of a function call returning an async iterator."""

    return [v async for v in fn(*args, **kwargs)]


##


def sync_await(
        fn: ta.Callable[P, ta.Awaitable[T]],
        *args: P.args,
        **kwargs: P.kwargs,
) -> T:
    """
    Allows for the synchronous execution of async functions which will never actually *externally* await anything. These
    functions are allowed to await any number of other functions - including contextmanagers and generators - so long as
    nothing ever actually 'leaks' out of the function, presumably to an event loop.
    """

    ret = missing = object()

    async def gate():
        nonlocal ret

        ret = await fn(*args, **kwargs)

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
        fn: ta.Callable[P, ta.AsyncIterator[T]],
        *args: P.args,
        **kwargs: P.kwargs,
) -> list[T]:
    """
    Uses `sync_await` to synchronously read the full contents of a function call returning an async iterator, given that
    the function never externally awaits anything.
    """

    lst: list[T] | None = None

    async def inner():
        nonlocal lst

        lst = [v async for v in fn(*args, **kwargs)]

    sync_await(inner)

    if not isinstance(lst, list):
        raise TypeError(lst)

    return lst
