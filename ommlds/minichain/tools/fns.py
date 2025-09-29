"""
TODO:
 - should really return Content conventionally
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl

from ..content.json import JsonContent
from ..content.types import Content


D = ta.TypeVar('D')


##


@dc.dataclass(frozen=True)
class ToolFn(lang.Final):
    @dc.dataclass(frozen=True)
    class Impl(lang.Sealed, lang.Abstract):
        pass

    @dc.dataclass(frozen=True, kw_only=True)
    class FnImpl(Impl):
        s: ta.Callable[..., ta.Any] | None = None
        a: ta.Callable[..., ta.Awaitable[ta.Any]] | None = None

        def __post_init__(self) -> None:
            if self.s is None and self.a is None:
                raise TypeError(f'one of s or a must be specified')

    @dc.dataclass(frozen=True)
    class MaysyncImpl(Impl):
        m: ta.Callable[..., ta.Awaitable[ta.Any]]

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
    class MarshalInput(Input, lang.Final):
        rtys: ta.Mapping[str, rfl.Type]

    @dc.dataclass(frozen=True)
    class RawKwargsInput(Input, lang.Final):
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
    class MarshalOutput(Output, lang.Final):
        rty: rfl.Type

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


async def execute_tool_fn(
        tfn: ToolFn,
        args: ta.Mapping[str, ta.Any],
        *,
        forbid_sync_as_async: bool = False,
) -> Content:
    m_fn: ta.Callable[..., ta.Awaitable[ta.Any]]
    if isinstance(tfn.impl, ToolFn.FnImpl):
        s_fn = tfn.impl.s
        if (a_fn := tfn.impl.a) is None and not forbid_sync_as_async and s_fn is not None:
            a_fn = lang.as_async(s_fn, wrap=True)
        m_fn = lang.make_maysync(
            s_fn if s_fn is not None else _no_sync_tool_impl,
            a_fn if a_fn is not None else _no_async_tool_impl,
        )
    elif isinstance(tfn.impl, ToolFn.MaysyncImpl):
        m_fn = tfn.impl.m
    else:
        raise TypeError(tfn.impl)

    #

    fn_kw: ta.Mapping[str, ta.Any]
    if isinstance(tfn.input, ToolFn.DataclassInput):
        raise NotImplementedError

    elif isinstance(tfn.input, ToolFn.MarshalInput):
        fn_kw_dct: dict[str, ta.Any] = {}
        for k, v in args.items():
            fn_kw_dct[k] = msh.unmarshal(v, tfn.input.rtys[k])
        fn_kw = fn_kw_dct

    elif isinstance(tfn.input, ToolFn.RawKwargsInput):
        fn_kw = args

    else:
        raise TypeError(tfn.input)

    #

    fn_out = await m_fn(**fn_kw)

    #

    ret: Content
    if isinstance(tfn.output, ToolFn.DataclassOutput):
        raise NotImplementedError

    elif isinstance(tfn.output, ToolFn.MarshalOutput):
        out_v = msh.marshal(fn_out, tfn.output.rty)
        ret = JsonContent(out_v)

    elif isinstance(tfn.output, ToolFn.RawStringOutput):
        ret = check.isinstance(fn_out, str)

    else:
        raise TypeError(tfn.output)

    #

    return ret
