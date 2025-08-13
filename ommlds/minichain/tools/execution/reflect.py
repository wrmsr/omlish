"""
TODO:
 - one-sided, sync ^ async, reflect sig
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
    if isinstance(fn, lang.Maysync_):
        impl = ToolFn.MaysyncImpl(fn.cast())
    else:
        # FIXME: assumes sync
        impl = ToolFn.FnImpl(fn, lang.as_async(fn))

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
