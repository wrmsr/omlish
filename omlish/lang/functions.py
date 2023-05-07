import functools
import typing as ta

from .descriptors import is_method_descriptor


def unwrap_func(fn: ta.Callable) -> ta.Callable:
    while True:
        if is_method_descriptor(fn):
            fn = fn.__func__  # type: ignore
        elif isinstance(fn, functools.partial):
            fn = fn.func
        else:
            nxt = getattr(fn, '__wrapped__', None)
            if not callable(nxt):
                return fn
            elif nxt is fn:
                raise TypeError(fn)
            fn = nxt
