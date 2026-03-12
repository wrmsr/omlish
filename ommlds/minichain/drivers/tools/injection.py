import typing as ta

from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang

from ...tools.execution.catalog import ToolCatalogEntries
from ...tools.execution.catalog import ToolCatalogEntry
from .configs import ToolSetConfig
from .execution import ToolContextProvider
from .execution import ToolContextProviders


ToolSetConfigT = ta.TypeVar('ToolSetConfigT', bound='ToolSetConfig')


##


@lang.cached_function
def tool_catalog_entries() -> inj.ItemsBinderHelper[ToolCatalogEntry]:
    return inj.items_binder_helper[ToolCatalogEntry](ToolCatalogEntries)


@lang.cached_function
def tool_context_providers() -> inj.ItemsBinderHelper[ToolContextProvider]:
    return inj.items_binder_helper[ToolContextProvider](ToolContextProviders)


def bind_tool_context_provider_to_key(key: ta.Any) -> inj.Elements:
    return tool_context_providers().bind_item(
        to_fn=inj.target(v=key)(lambda v: ToolContextProvider(lambda: [v])),
        singleton=True,
    )


##


@dc.dataclass(frozen=True)
class ToolSetBinder(lang.Final, ta.Generic[ToolSetConfigT]):
    cfg_cls: type[ToolSetConfig]
    fn: ta.Callable[[ToolSetConfigT], inj.Elements]
