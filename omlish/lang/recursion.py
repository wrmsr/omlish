import contextlib
import dataclasses as dc
import functools
import threading
import typing as ta


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


_LOCK = threading.RLock()
_LOCAL: threading.local


def _local() -> threading.local:
    global _LOCAL

    try:
        return _LOCAL
    except NameError:
        pass

    with _LOCK:
        try:
            return _LOCAL
        except NameError:
            pass

        _LOCAL = threading.local()
        return _LOCAL


def _depth_map() -> dict[ta.Any, int]:
    lo = _local()
    try:
        return lo.depth_map
    except AttributeError:
        dm = lo.depth_map = {}
        return dm


##


@dc.dataclass()
class LimitedRecursionError(RecursionError):
    key: ta.Any
    depth: int


@contextlib.contextmanager
def recursion_limiting_context(key: ta.Any, limit: int | None) -> ta.Iterator[int | None]:
    if limit is None:
        yield None
        return

    dm = _depth_map()

    try:
        pd: int | None = dm[key]
    except KeyError:
        pd = None
    else:
        if not isinstance(pd, int) and pd > 0:  # type: ignore[operator]
            raise RuntimeError

    if pd is not None and pd >= limit:
        raise LimitedRecursionError(key, pd)

    nd = (pd or 0) + 1
    dm[key] = nd

    try:
        yield nd

    finally:
        if dm.get(key) != nd:
            raise RuntimeError

        if pd is not None:
            dm[key] = pd
        else:
            del dm[key]


##


def recursion_limiting(limit: int | None) -> ta.Callable[[ta.Callable[P, T]], ta.Callable[P, T]]:
    def outer(fn):
        if not callable(fn):
            raise TypeError(fn)

        if limit is None:
            return fn

        @functools.wraps(fn)
        def inner(*args, **kwargs):
            with recursion_limiting_context(fn, limit):
                return fn(*args, **kwargs)

        return inner

    return outer
