"""
TODO:
 - async<->sync greeenlet bridge
  In [5]: %timeit greenlet.greenlet(f).switch()
  517 ns ± 13.2 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
  - injected io provider - sync vs greenlet aio trampolined
 - push/pull bridge?

https://github.com/sqlalchemy/sqlalchemy/blob/1e75c189da721395bc8c2d899c722a5b9a170404/lib/sqlalchemy/util/_concurrency_py3k.py#L83
"""
import concurrent.futures as cf
import contextlib
import functools
import time
import typing as ta


T = ta.TypeVar('T')
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)


def sync_await(fn: ta.Callable[..., T], *args, **kwargs) -> T:
    ret: ta.Any
    ret = missing = object()

    async def gate():
        nonlocal ret
        ret = await fn(*args, **kwargs)  # type: ignore

    cr = gate()
    with contextlib.closing(cr):
        try:
            cr.send(None)
        except StopIteration:
            pass
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


class ImmediateExecutor(cf.Executor):

    def __init__(self, *, immediate_exceptions: bool = False) -> None:
        super().__init__()
        self._immediate_exceptions = immediate_exceptions

    def submit(self, fn, *args, **kwargs):
        future: ta.Any = cf.Future()
        try:
            result = fn(*args, **kwargs)
            future.set_result(result)
        except Exception as e:
            if self._immediate_exceptions:
                raise
            future.set_exception(e)
        return future


class AsyncTimeoutException(Exception):
    pass


class FutureException(Exception, ta.Generic[T]):

    def __init__(self, future: cf.Future, target: ta.Optional[T] = None) -> None:
        super().__init__()

        self._future = future
        self._target = target

    @property
    def future(self) -> cf.Future:
        return self._future

    @property
    def target(self) -> ta.Optional[T]:
        return self._target

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__qualname__}('
            f'exception={self._future.exception()!r}, '
            f'future={self._future!r}, '
            f'target={self._target})'
        )

    __str__ = __repr__


def await_futures(
        futures: ta.Sequence[cf.Future],
        *,
        timeout_s: ta.Union[int, float] = 60,
        tick_interval_s: ta.Union[int, float] = 0.5,
        tick_fn: ta.Callable[..., bool] = lambda: True,
        raise_exceptions: bool = False,
        cancel_on_exception: bool = False,
) -> bool:
    start = time.time()

    not_done = set(futures)
    while tick_fn():
        done = {f for f in not_done if f.done()}
        if raise_exceptions:
            for fut in done:
                if fut.exception():
                    if cancel_on_exception:
                        for cancel_fut in not_done:
                            cancel_fut.cancel()
                    raise FutureException(fut) from fut.exception()

        not_done -= done
        if not not_done:
            return True

        if time.time() >= (start + timeout_s):
            raise AsyncTimeoutException
        time.sleep(tick_interval_s)

    return False


def await_dependent_futures(
        executor: cf.Executor,
        dependency_sets_by_fn: ta.Mapping[ta.Callable, ta.AbstractSet[ta.Callable]],
        *,
        timeout_s: ta.Union[int, float] = 60,
        tick_interval_s: ta.Union[int, float] = 0.5,
        tick_fn: ta.Callable[..., bool] = lambda: True,
) -> ta.Mapping[ta.Callable, cf.Future]:
    for fn, deps in dependency_sets_by_fn.items():
        for dep in deps:
            if dep == fn:
                raise ValueError(fn)
            if dep not in dependency_sets_by_fn:
                raise KeyError(dep)
            if fn in dependency_sets_by_fn[dep]:
                raise Exception(f'Cyclic dependencies: {fn} <-> {dep}', fn, dep)

    dependent_sets_by_fn: ta.Dict[ta.Callable, ta.Set[ta.Callable]] = {fn: set() for fn in dependency_sets_by_fn}
    for fn, deps in dependency_sets_by_fn.items():
        for dep in deps:
            dependent_sets_by_fn[dep].add(fn)
    remaining_dep_sets_by_fn = {
        fn: set(dependencies) for fn, dependencies in dependency_sets_by_fn.items()
    }
    root_fns = {fn for fn, deps in remaining_dep_sets_by_fn.items() if not deps}
    fns_by_fut = {fut: fn for fn in root_fns for fut in [executor.submit(fn)] if fut is not None}

    def cancel():
        for cancel_fut in fns_by_fut:
            cancel_fut.cancel()

    start = time.time()
    not_done = set(fns_by_fut.keys())
    while not_done and tick_fn():
        done, not_done = cf.wait(not_done, timeout=tick_interval_s, return_when=cf.FIRST_COMPLETED)
        not_done = set(not_done)

        for fut in done:
            if fut.exception():
                cancel()
                raise FutureException(fut) from fut.exception()

            fn = fns_by_fut[fut]
            for dependent_fn in dependent_sets_by_fn.get(fn, set()):
                remaining_deps = remaining_dep_sets_by_fn[dependent_fn]
                remaining_deps.remove(fn)
                if not remaining_deps:
                    downstream_fut = executor.submit(dependent_fn)
                    if downstream_fut is not None:
                        fns_by_fut[downstream_fut] = dependent_fn
                        not_done.add(downstream_fut)

        if time.time() >= (start + timeout_s):
            cancel()
            raise AsyncTimeoutException

    remaining_fns = {fn: deps for fn, deps in remaining_dep_sets_by_fn.items() if deps}
    if remaining_fns:
        raise Exception(f"Unfinished fns: {remaining_fns}", remaining_fns)

    futs_by_fn = {fn: fut for fut, fn in fns_by_fut.items()}
    return futs_by_fn
