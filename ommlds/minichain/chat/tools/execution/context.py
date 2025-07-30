import contextlib
import contextvars
import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True)
class ToolContext(lang.Final):
    dct: col.TypeMap = col.TypeMap()


_TOOL_CONTEXT: contextvars.ContextVar[ToolContext] = contextvars.ContextVar(f'{__name__}._TOOL_CONTEXT')


@contextlib.contextmanager
def bind_tool_context(ctx: ToolContext) -> ta.Generator[ToolContext]:
    try:
        cur = _TOOL_CONTEXT.get()
    except LookupError:
        pass
    else:
        raise RuntimeError(f'Already bound: {cur}')

    tok = _TOOL_CONTEXT.set(ctx)
    try:
        yield ctx
    finally:
        _TOOL_CONTEXT.reset(tok)


def tool_context() -> ToolContext:
    return _TOOL_CONTEXT.get()
