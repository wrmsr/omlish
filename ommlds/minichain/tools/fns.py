"""
TODO:
 - should really return Content conventionally
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


D = ta.TypeVar('D')


##


@dc.dataclass(frozen=True)
class ToolFn(lang.Final):
    fn: ta.Callable | lang.Maysync_

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


##


@lang.maysync
async def m_execute_tool_fn(
        tfn: ToolFn,
        args: ta.Mapping[str, ta.Any],
) -> str:
    m_fn: lang.Maysync
    if isinstance(tfn.fn, lang.Maysync_):
        m_fn = ta.cast(ta.Any, tfn)
    else:
        m_fn = lang.make_maysync(tfn.fn)

    out: ta.Any
    if isinstance(tfn.input, ToolFn.DataclassInput):
        raise NotImplementedError
    elif isinstance(tfn.input, ToolFn.KwargsInput):
        out = await m_fn(**args).m()
    else:
        raise NotImplementedError

    ret: str
    if isinstance(tfn.output, ToolFn.DataclassOutput):
        raise NotImplementedError
    elif isinstance(tfn.output, ToolFn.RawStringOutput):
        ret = check.isinstance(out, str)
    else:
        raise NotImplementedError

    return ret
