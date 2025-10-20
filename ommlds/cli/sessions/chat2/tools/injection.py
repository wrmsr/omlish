import typing as ta

from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc


with lang.auto_proxy_import(globals()):
    from . import execution as _execution

##


@lang.cached_function
def tool_catalog_entries() -> 'inj.ItemsBinderHelper[mc.ToolCatalogEntry]':
    return inj.items_binder_helper[mc.ToolCatalogEntry](mc.ToolCatalogEntries)


@lang.cached_function
def tool_context_providers() -> 'inj.ItemsBinderHelper[_execution.ToolContextProvider]':
    return inj.items_binder_helper[_execution.ToolContextProvider](_execution.ToolContextProviders)


def bind_tool_context_provider_to_key(key: ta.Any) -> inj.Elements:
    return tool_context_providers().bind_item(to_fn=inj.KwargsTarget.of(
        lambda v: _execution.ToolContextProvider(lambda: [v]),
        v=key,
    ), singleton=True)
