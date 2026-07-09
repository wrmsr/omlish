"""
TODO:
 - ta.type_hints
"""
import inspect
import typing as ta

from omlish import contextual as cxl
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
        include_contextual_params: bool = False,
) -> ToolCatalogEntry:
    impl: ToolFn.Impl
    if lang.is_maysync(fn):
        impl = ToolFn.MaysyncImpl(fn)
    elif inspect.iscoroutinefunction(lang.unwrap_callable(fn)):
        impl = ToolFn.FnImpl(a=fn)
    else:
        impl = ToolFn.FnImpl(s=fn, a=lang.as_async(fn, wrap=True))

    #

    sig = inspect.signature(fn)

    tf_input: ToolFn.Input
    if marshal_input:
        in_rtys: dict[str, rfl.Type] = {}
        for p in sig.parameters.values():
            # FIXME: dedupe vs ToolReflector
            if not include_contextual_params and cxl.is_unbound_param(p.default):
                continue
            p_rty = rfl.reflect_type(p.annotation)
            if not no_marshal_check:
                msh.global_marshaling().new_unmarshal_factory_context().make_unmarshaler(p_rty)
            in_rtys[p.name] = p_rty
        tf_input = ToolFn.MarshalInput(in_rtys)
    else:
        tf_input = ToolFn.RawKwargsInput()

    #

    tf_output: ToolFn.Output
    if marshal_output:
        out_rty = rfl.reflect_type(sig.return_annotation)
        if not no_marshal_check:
            msh.global_marshaling().new_marshal_factory_context().make_marshaler(out_rty)
        tf_output = ToolFn.MarshalOutput(out_rty)
    else:
        if sig.return_annotation is not str:
            raise NotImplementedError(fn)
        tf_output = ToolFn.RawStringOutput()

    #

    context = {
        p.annotation
        for p in sig.parameters.values()
        if cxl.is_unbound_param(p.default)
    }

    #

    return ToolCatalogEntry(
        reflect_tool_spec(
            fn,
            include_contextual_params=include_contextual_params,
        ),
        ToolFn(
            impl,
            tf_input,
            tf_output,
            context=frozenset(context) if context else None,
        ),
    )
