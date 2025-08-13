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
    @dc.dataclass(frozen=True)
    class Impl(lang.Sealed, lang.Abstract):
        pass

    @dc.dataclass(frozen=True)
    class FnImpl(Impl):
        s: ta.Callable[..., ta.Any] | None = None
        a: ta.Callable[..., ta.Awaitable[ta.Any]] | None = None

        def __post_init__(self) -> None:
            if self.s is None and self.a is None:
                raise TypeError(f'one of s or a must be specified')

    @dc.dataclass(frozen=True)
    class MaysyncImpl(Impl):
        m: lang.Maysync

    impl: Impl

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


class NoToolImplError(Exception):
    pass


def _no_sync_tool_impl(*args, **kwargs):
    raise NoToolImplError


async def _no_async_tool_impl(*args, **kwargs):
    raise NoToolImplError


##


@lang.maysync
async def m_execute_tool_fn(
        tfn: ToolFn,
        args: ta.Mapping[str, ta.Any],
) -> str:
    m_fn: lang.Maysync
    if isinstance(tfn.impl, ToolFn.FnImpl):
        m_fn = lang.make_maysync(
            tfn.impl.s if tfn.impl.s is not None else _no_sync_tool_impl,
            tfn.impl.a if tfn.impl.a is not None else _no_async_tool_impl,
        )
    elif isinstance(tfn.impl, ToolFn.MaysyncImpl):
        m_fn = tfn.impl.m
    else:
        raise TypeError(tfn.impl)

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
