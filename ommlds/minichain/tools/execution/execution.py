import typing as ta

from omlish import check

from .context import ToolContext
from .context import bind_tool_context
from .types import ToolFn


##


def _execute_tool_fn(
        te: ToolFn,
        args: ta.Mapping[str, ta.Any],
) -> str:
    fn = te.fn

    out: ta.Any
    if isinstance(te.input, ToolFn.DataclassInput):
        raise NotImplementedError
    elif isinstance(te.input, ToolFn.KwargsInput):
        out = fn(**args)
    else:
        raise NotImplementedError

    ret: str
    if isinstance(te.output, ToolFn.DataclassOutput):
        raise NotImplementedError
    elif isinstance(te.output, ToolFn.RawStringOutput):
        ret = check.isinstance(out, str)
    else:
        raise NotImplementedError

    return ret


def execute_tool_fn(
        ctx: ToolContext,
        te: ToolFn,
        args: ta.Mapping[str, ta.Any],
) -> str:
    with bind_tool_context(ctx):
        return _execute_tool_fn(te, args)
