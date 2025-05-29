import dataclasses as dc
import typing as ta

from omlish import check
from omlish import inject as inj

from ... import minichain as mc
from ..sessions.inject import bind_chat_options
from .tools import WEATHER_TOOL
from .tools import Tool
from .tools import ToolMap


##


@dc.dataclass(frozen=True, eq=False)
class InjectedTool:
    t: Tool


def bind_tool(tool: Tool) -> inj.Element | inj.Elements:
    it = InjectedTool(tool)
    it_key: inj.Key = inj.Key(InjectedTool, tag=inj.Id(id(it)))

    return inj.as_elements(
        inj.bind(it_key, to_const=it),
        inj.set_binder[InjectedTool]().bind(it_key),

        bind_chat_options(mc.Tool(tool.spec)),
    )


def provide_tool_map(its: ta.AbstractSet[InjectedTool]) -> ToolMap:
    dct: dict[str, Tool] = {}
    for it in its:
        check.not_in(it.t.spec.name, dct)
        dct[it.t.spec.name] = it.t
    return ToolMap(dct)


##


def bind_tools(
        *,
        enable_test_weather_tool: bool = False,
) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.set_binder[InjectedTool](),
        inj.bind(provide_tool_map, singleton=True),
    ]

    #

    if enable_test_weather_tool:
        els.append(bind_tool(WEATHER_TOOL))

    #

    return inj.as_elements(*els)
