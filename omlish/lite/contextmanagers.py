# ruff: noqa: UP007
import contextlib
import typing as ta

from .check import check


T = ta.TypeVar('T')
ExitStackedT = ta.TypeVar('ExitStackedT', bound='ExitStacked')


##


class ExitStacked:
    _exit_stack: ta.Optional[contextlib.ExitStack] = None

    def __enter__(self: ExitStackedT) -> ExitStackedT:
        check.state(self._exit_stack is None)
        es = self._exit_stack = contextlib.ExitStack()
        es.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (es := self._exit_stack) is None:
            return None
        self._exit_contexts()
        return es.__exit__(exc_type, exc_val, exc_tb)

    def _exit_contexts(self) -> None:
        pass

    def _enter_context(self, cm: ta.ContextManager[T]) -> T:
        es = check.not_none(self._exit_stack)
        return es.enter_context(cm)


##


@contextlib.contextmanager
def defer(fn: ta.Callable) -> ta.Generator[ta.Callable, None, None]:
    try:
        yield fn
    finally:
        fn()


@contextlib.contextmanager
def attr_setting(obj, attr, val, *, default=None):  # noqa
    not_set = object()
    orig = getattr(obj, attr, not_set)
    try:
        setattr(obj, attr, val)
        if orig is not not_set:
            yield orig
        else:
            yield default
    finally:
        if orig is not_set:
            delattr(obj, attr)
        else:
            setattr(obj, attr, orig)


##


class aclosing(contextlib.AbstractAsyncContextManager):  # noqa
    def __init__(self, thing):
        self.thing = thing

    async def __aenter__(self):
        return self.thing

    async def __aexit__(self, *exc_info):
        await self.thing.aclose()
