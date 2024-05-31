import contextlib
import types
import typing as ta

from .classes import Virtual


T = ta.TypeVar('T')


##


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


class NopContextManaged(ContextManaged):

    def __init_subclass__(cls, **kwargs):
        raise TypeError


NOP_CONTEXT_MANAGED = NopContextManaged()


class NopContextManager:

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    def __call__(self, *args, **kwargs):
        return NOP_CONTEXT_MANAGED


NOP_CONTEXT_MANAGER = NopContextManager()


##


class ContextManager(Virtual, ta.Generic[T]):

    def __enter__(self) -> T:
        raise NotImplementedError

    def __exit__(
            self,
            exc_type: ta.Optional[ta.Type[Exception]],
            exc_val: ta.Optional[Exception],
            exc_tb: ta.Optional[types.TracebackType]
    ) -> ta.Optional[bool]:
        raise NotImplementedError


##


@contextlib.contextmanager
def defer(fn: ta.Callable) -> ta.Iterator[ta.Callable]:
    try:
        yield fn
    finally:
        fn()


@contextlib.contextmanager
def maybe_managing(obj: T) -> ta.Iterator[T]:
    if isinstance(obj, ContextManager):
        with obj:
            yield ta.cast(T, obj)
    else:
        yield obj


@contextlib.contextmanager
def disposing(obj: T, attr: str = 'dispose') -> ta.Iterator[T]:
    try:
        yield obj
    finally:
        getattr(obj, attr)()


