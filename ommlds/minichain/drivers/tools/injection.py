import typing as ta

from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang

from .configs import ToolSetConfig


with lang.auto_proxy_import(globals()):
    from ...tools.execution import catalog as _tools_execution_catalog
    from . import execution as _execution


ToolSetConfigT = ta.TypeVar('ToolSetConfigT', bound='ToolSetConfig')


##


@lang.cached_function
def tool_catalog_entries() -> 'inj.ItemsBinderHelper[_tools_execution_catalog.ToolCatalogEntry]':
    return inj.items_binder_helper[_tools_execution_catalog.ToolCatalogEntry](_tools_execution_catalog.ToolCatalogEntries)  # noqa


@lang.cached_function
def tool_context_providers() -> 'inj.ItemsBinderHelper[_execution.ToolContextProvider]':
    return inj.items_binder_helper[_execution.ToolContextProvider](_execution.ToolContextProviders)


def bind_tool_context_provider_to_key(key: ta.Any) -> inj.Elements:
    return tool_context_providers().bind_item(
        to_fn=inj.target(v=key)(lambda v: _execution.ToolContextProvider(lambda: [v])),
        singleton=True,
    )


##


@dc.dataclass(frozen=True)
class ToolSetBinder(lang.Final, ta.Generic[ToolSetConfigT]):
    cfg_cls: type[ToolSetConfig]
    fn: ta.Callable[[ToolSetConfigT], inj.Elements]
