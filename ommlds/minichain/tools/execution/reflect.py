"""
TODO:
"""
import inspect
import typing as ta

from omlish import lang

from ..fns import ToolFn
from ..reflect import reflect_tool_spec
from .catalog import ToolCatalogEntry


##


def reflect_tool_catalog_entry(fn: ta.Callable) -> ToolCatalogEntry:
    impl: ToolFn.Impl
    if lang.is_maysync(fn):
        impl = ToolFn.MaysyncImpl(fn)
    elif inspect.iscoroutinefunction(lang.unwrap_callable(fn)):
        impl = ToolFn.FnImpl(a=fn)
    else:
        impl = ToolFn.FnImpl(s=fn, a=lang.as_async(fn, wrap=True))

    sig = inspect.signature(fn)
    if sig.return_annotation is not str:
        raise NotImplementedError(fn)

    return ToolCatalogEntry(
        reflect_tool_spec(fn),
        ToolFn(
            impl,
            ToolFn.KwargsInput(),
            ToolFn.RawStringOutput(),
        ),
    )
