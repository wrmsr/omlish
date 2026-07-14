from omcore import inject as inj
from omcore import lang

from ...tools.execution.catalog import ToolCatalogEntry
from ...tools.execution.injection import tool_catalog_entries
from ...tools.execution.reflect import reflect_tool_catalog_entry
from .configs import WebConfig


with lang.auto_proxy_import(globals()):
    from . import fetching as _fetching
    from .tools import fetch as _fetch_tool
    from .tools import search as _search_tool


##


def bind_web(cfg: WebConfig = WebConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(inj.bind(_fetching.WebFetcher, to_ctor=_fetching.HttpWebFetcher, singleton=True))

    def _provide_web_fetch_tool_catalog_entry(tool: _fetch_tool.WebFetchTool) -> ToolCatalogEntry:
        return reflect_tool_catalog_entry(tool.web_fetch)

    els.extend([
        inj.bind(_fetch_tool.WebFetchTool, singleton=True),
        tool_catalog_entries().bind_item(to_fn=_provide_web_fetch_tool_catalog_entry, singleton=True),
    ])

    #

    if cfg.enable_search:
        def _provide_web_search_tool_catalog_entry(tool: _search_tool.WebSearchTool) -> ToolCatalogEntry:
            return reflect_tool_catalog_entry(tool.web_search)

        els.extend([
            inj.bind(_search_tool.WebSearchTool, singleton=True),
            tool_catalog_entries().bind_item(to_fn=_provide_web_search_tool_catalog_entry, singleton=True),
        ])

    #

    return inj.as_elements(*els)
