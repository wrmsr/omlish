import contextlib
import typing as ta


@contextlib.contextmanager
def defer(fn: ta.Callable) -> ta.Iterator[ta.Callable]:
    try:
        yield fn
    finally:
        fn()


def attr_repr(obj: ta.Any, *attrs: str) -> str:
    return '%s(%s)' % (
        type(obj).__name__,
        ', '.join('%s=%r' % (attr, getattr(obj, attr)) for attr in attrs))


def arg_repr(*args, **kwargs) -> str:
    return ', '.join(*(
            list(map(repr, args)) +
            [f'{k}={repr(v)}' for k, v in kwargs.items()]
    ))
