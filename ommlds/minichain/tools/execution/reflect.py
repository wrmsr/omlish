import inspect
import typing as ta

from ..fns import ToolFn
from ..reflect import reflect_tool_spec
from .catalog import ToolCatalogEntry


##


def reflect_tool_catalog_entry(fn: ta.Callable) -> ToolCatalogEntry:
    sig = inspect.signature(fn)
    if sig.return_annotation is not str:
        raise NotImplementedError(fn)

    return ToolCatalogEntry(
        reflect_tool_spec(fn),
        ToolFn(
            fn,
            ToolFn.KwargsInput(),
            ToolFn.RawStringOutput(),
        ),
    )
