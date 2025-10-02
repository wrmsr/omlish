"""
TODO:
 - ta.type_hints
"""
import inspect
import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl

from ..fns import ToolFn
from ..reflect import reflect_tool_spec
from .catalog import ToolCatalogEntry


##


def reflect_tool_catalog_entry(
        fn: ta.Callable,
        *,
        marshal_input: bool = False,
        marshal_output: bool = False,
        no_marshal_check: bool = False,
) -> ToolCatalogEntry:
    impl: ToolFn.Impl
    if lang.is_maysync(fn):
        impl = ToolFn.MaysyncImpl(fn)
    elif inspect.iscoroutinefunction(lang.unwrap_callable(fn)):
        impl = ToolFn.FnImpl(a=fn)
    else:
        impl = ToolFn.FnImpl(s=fn, a=lang.as_async(fn, wrap=True))

    #

    tf_input: ToolFn.Input
    sig = inspect.signature(fn)
    if marshal_input:
        in_rtys: dict[str, rfl.Type] = {}
        for p in sig.parameters.values():
            p_rty = rfl.type_(p.annotation)
            if not no_marshal_check:
                msh.global_marshaling().new_unmarshal_factory_context().make_unmarshaler(p_rty)
            in_rtys[p.name] = p_rty
        tf_input = ToolFn.MarshalInput(in_rtys)
    else:
        tf_input = ToolFn.RawKwargsInput()

    #

    tf_output: ToolFn.Output
    if marshal_output:
        out_rty = rfl.type_(sig.return_annotation)
        if not no_marshal_check:
            msh.global_marshaling().new_marshal_factory_context().make_marshaler(out_rty)
        tf_output = ToolFn.MarshalOutput(out_rty)
    else:
        if sig.return_annotation is not str:
            raise NotImplementedError(fn)
        tf_output = ToolFn.RawStringOutput()

    #

    return ToolCatalogEntry(
        reflect_tool_spec(fn),
        ToolFn(
            impl,
            tf_input,
            tf_output,
        ),
    )
