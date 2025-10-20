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
