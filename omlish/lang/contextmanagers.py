import contextlib
import typing as ta


@contextlib.contextmanager
def defer(fn: ta.Callable) -> ta.Iterator[ta.Callable]:
    try:
        yield fn
    finally:
        fn()
