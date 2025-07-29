import contextlib
import contextvars
import typing as ta

from omlish import lang


##


class ToolContext(lang.Final):
    pass


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
