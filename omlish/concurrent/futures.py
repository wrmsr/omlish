import concurrent.futures as cf
import time
import typing as ta


T = ta.TypeVar('T')


##


class FutureError(Exception, ta.Generic[T]):
    def __init__(self, future: cf.Future, target: T | None = None) -> None:
        super().__init__()

        self._future = future
        self._target = target

    @property
    def future(self) -> cf.Future:
        return self._future

    @property
    def target(self) -> T | None:
        return self._target

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__qualname__}('
            f'exception={self._future.exception()!r}, '
            f'future={self._future!r}, '
            f'target={self._target})'
        )

    __str__ = __repr__


class FutureTimeoutError(Exception):
    pass


def wait_futures(
        futures: ta.Sequence[cf.Future],
        *,
        timeout_s: float = 60,
        tick_interval_s: float = .5,
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
                    raise FutureError(fut) from fut.exception()

        not_done -= done
        if not not_done:
            return True

        if time.time() >= (start + timeout_s):
            raise FutureTimeoutError
        time.sleep(tick_interval_s)

    return False


def wait_dependent_futures(
        executor: cf.Executor,
        dependency_sets_by_fn: ta.Mapping[ta.Callable, ta.AbstractSet[ta.Callable]],
        *,
        timeout_s: float = 60,
        tick_interval_s: float = .5,
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

    dependent_sets_by_fn: dict[ta.Callable, set[ta.Callable]] = {fn: set() for fn in dependency_sets_by_fn}
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
                raise FutureError(fut) from fut.exception()

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
            raise FutureTimeoutError

    remaining_fns = {fn: deps for fn, deps in remaining_dep_sets_by_fn.items() if deps}
    if remaining_fns:
        raise Exception(f'Unfinished fns: {remaining_fns}', remaining_fns)

    futs_by_fn = {fn: fut for fut, fn in fns_by_fut.items()}
    return futs_by_fn
