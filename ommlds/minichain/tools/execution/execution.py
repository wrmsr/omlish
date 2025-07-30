import typing as ta

from omlish import check

from .context import ToolContext
from .context import bind_tool_context
from .types import ToolExecutor


##


def _execute_tool_executor(
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


def execute_tool_executor(
        ctx: ToolContext,
        te: ToolExecutor,
        args: ta.Mapping[str, ta.Any],
) -> str:
    with bind_tool_context(ctx):
        return _execute_tool_executor(te, args)
