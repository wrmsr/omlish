import contextlib
import types
import typing as ta


class ContextManaged:

    def __enter__(self: ta.Self) -> ta.Self:
        return self

    def __exit__(
            self,
            exc_type: ta.Optional[ta.Type[Exception]],
            exc_val: ta.Optional[Exception],
            exc_tb: ta.Optional[types.TracebackType]
    ) -> ta.Optional[bool]:
        return None


@contextlib.contextmanager
def defer(fn: ta.Callable) -> ta.Iterator[ta.Callable]:
    try:
        yield fn
    finally:
        fn()
