import contextlib
import typing as ta


def raise_(o: BaseException) -> ta.NoReturn:
    raise o


@contextlib.contextmanager
def defer(fn: ta.Callable) -> ta.Iterator[ta.Callable]:
    try:
        yield fn
    finally:
        fn()
