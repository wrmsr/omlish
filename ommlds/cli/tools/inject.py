import dataclasses as dc
import typing as ta

from omlish import inject as inj

from ... import minichain as mc
from ..sessions.chat.inject import bind_chat_options
from .weather import WEATHER_TOOL


##


@dc.dataclass(frozen=True, eq=False)
class _InjectedTool:
    tce: mc.ToolCatalogEntry


def bind_tool(tce: mc.ToolCatalogEntry) -> inj.Element | inj.Elements:
    it = _InjectedTool(tce)
    it_key: inj.Key = inj.Key(_InjectedTool, tag=inj.Id(id(it)))

    return inj.as_elements(
        inj.bind(it_key, to_const=it),
        inj.set_binder[_InjectedTool]().bind(it_key),

        bind_chat_options(mc.Tool(tce.spec)),
    )


def _provide_tool_catalog(its: ta.AbstractSet[_InjectedTool]) -> mc.ToolCatalog:
    return mc.ToolCatalog(ta.cast(mc.ToolCatalogEntries, [it.tce for it in its]))


##


def bind_tools(
        *,
        enable_test_weather_tool: bool = False,
) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.set_binder[_InjectedTool](),
        inj.bind(_provide_tool_catalog, singleton=True),
    ]

    #

    if enable_test_weather_tool:
        els.append(bind_tool(WEATHER_TOOL))

    #

    return inj.as_elements(*els)
