import typing as ta

from omcore import inject as inj
from omcore import lang

from ...tools.execution.catalog import ToolCatalogEntries
from ...tools.execution.catalog import ToolCatalogEntry
from .context import ToolContextProvider
from .context import ToolContextProviders


##


@lang.cached_function
def tool_catalog_entries() -> inj.ItemsBinderHelper[ToolCatalogEntry]:
    return inj.items_binder_helper[ToolCatalogEntry](ToolCatalogEntries)


@lang.cached_function
def tool_context_providers() -> inj.ItemsBinderHelper[ToolContextProvider]:
    return inj.items_binder_helper[ToolContextProvider](ToolContextProviders)


def bind_tool_context_provider_to_key(ty: type, key: ta.Any | None = None) -> inj.Elements:
    if key is None:
        key = ty
    return tool_context_providers().bind_item(
        to_fn=inj.target(v=key)(lambda v: ToolContextProvider(ty, lambda: v)),
        singleton=True,
    )
