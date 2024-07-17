"""
TODO:
 - async<->sync greeenlet bridge
  In [5]: %timeit greenlet.greenlet(f).switch()
  517 ns ± 13.2 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
  - injected io provider - sync vs greenlet aio trampolined
 - push/pull bridge?

https://github.com/sqlalchemy/sqlalchemy/blob/1e75c189da721395bc8c2d899c722a5b9a170404/lib/sqlalchemy/util/_concurrency_py3k.py#L83
"""
import contextlib
import functools
import typing as ta


T = ta.TypeVar('T')


def sync_await(fn: ta.Callable[..., T], *args, **kwargs) -> T:
    ret: ta.Any
    ret = missing = object()

    async def gate():
        nonlocal ret
        ret = await fn(*args, **kwargs)  # type: ignore

    cr = gate()
    with contextlib.closing(cr):
        with contextlib.suppress(StopIteration):
            cr.send(None)
        if ret is missing or cr.cr_await is not None or cr.cr_running:
            raise TypeError('Not terminated')

    return ta.cast(T, ret)


def sync_list(fn: ta.Callable[..., ta.AsyncIterator[T]], *args, **kwargs) -> list[T]:
    lst = None

    async def inner():
        nonlocal lst
        lst = [v async for v in fn(*args, **kwargs)]

    sync_await(inner)
    if not isinstance(lst, list):
        raise TypeError(lst)
    return lst


async def async_list(fn: ta.Callable[..., ta.AsyncIterator[T]], *args, **kwargs) -> list[T]:
    return [v async for v in fn(*args, **kwargs)]


class SyncableIterable(ta.Generic[T]):

    def __init__(self, obj) -> None:
        super().__init__()
        self._obj = obj

    def __iter__(self) -> ta.Iterator[T]:
        async def inner():
            async for i in self._obj:
                yield i
        return iter(sync_list(inner))

    def __aiter__(self) -> ta.AsyncIterator[T]:
        return self._obj.__aiter__()


def syncable_iterable(fn: ta.Callable[..., ta.AsyncIterator[T]]) -> ta.Callable[..., SyncableIterable[T]]:
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        return SyncableIterable(fn(*args, **kwargs))
    return inner
