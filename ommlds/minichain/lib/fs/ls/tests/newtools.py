import contextlib
import contextvars
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


D = ta.TypeVar('D')
R = ta.TypeVar('R')
T = ta.TypeVar('T')


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


##


@dc.dataclass(frozen=True)
class ToolExecutor(lang.Final):
    fn: ta.Callable

    #

    @dc.dataclass(frozen=True)
    class Input(lang.Sealed, lang.Abstract):
        pass

    @dc.dataclass(frozen=True)
    class DataclassInput(Input, lang.Final, ta.Generic[D]):
        cls: type[D]

        def __post_init__(self) -> None:
            check.isinstance(self.cls, type)
            check.arg(dc.is_dataclass(self.cls))

    @dc.dataclass(frozen=True)
    class KwargsInput(Input, lang.Final):
        pass

    input: Input

    #

    @dc.dataclass(frozen=True)
    class Output(lang.Sealed, lang.Abstract):
        pass

    @dc.dataclass(frozen=True)
    class DataclassOutput(Output, lang.Final, ta.Generic[D]):
        cls: type[D]

        def __post_init__(self) -> None:
            check.isinstance(self.cls, type)
            check.arg(dc.is_dataclass(self.cls))

    @dc.dataclass(frozen=True)
    class RawStringOutput(Output, lang.Final):
        pass

    output: Output


#


def execute_tool_executor(
        te: ToolExecutor,
        args: ta.Mapping[str, ta.Any],
) -> str:
    fn = te.fn

    out: ta.Any
    if isinstance(te.input, ToolExecutor.DataclassInput):
        raise NotImplementedError
    elif isinstance(te.input, ToolExecutor.KwargsInput):
        out = fn(**args)
    else:
        raise NotImplementedError

    ret: str
    if isinstance(te.output, ToolExecutor.DataclassOutput):
        raise NotImplementedError
    elif isinstance(te.output, ToolExecutor.RawStringOutput):
        ret = check.isinstance(out, str)
    else:
        raise NotImplementedError

    return ret
