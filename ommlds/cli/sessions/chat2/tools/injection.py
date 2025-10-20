from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc


##


@lang.cached_function
def tool_catalog_entries() -> 'inj.ItemsBinderHelper[mc.ToolCatalogEntry]':
    return inj.items_binder_helper[mc.ToolCatalogEntry](mc.ToolCatalogEntries)
