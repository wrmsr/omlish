import dataclasses as dc
import typing as ta

from omlish import inject as inj
from omlish import lang

from ... import minichain as mc
from ..sessions.chat.inject import bind_chat_options
from .config import ToolsConfig
from .weather import WEATHER_TOOL


##


@dc.dataclass(frozen=True, eq=False)
class _InjectedTool:
    tce: mc.ToolCatalogEntry


def bind_tool(tce: mc.ToolCatalogEntry) -> inj.Element | inj.Elements:
    return inj.as_elements(
        inj.bind_set_entry_const(ta.AbstractSet[_InjectedTool], _InjectedTool(tce)),

        bind_chat_options(mc.Tool(tce.spec)),
    )


##


def bind_tools(tools_config: ToolsConfig) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(tools_config),

        inj.bind(mc.ToolCatalog, singleton=True),

        inj.set_binder[_InjectedTool](),
        inj.bind(
            lang.typed_lambda(mc.ToolCatalogEntries, s=ta.AbstractSet[_InjectedTool])(
                lambda s: [it.tce for it in s],
            ),
            singleton=True,
        ),
    ]

    #

    if tools_config.enable_fs_tools:
        from ...minichain.lib.fs.tools.ls import ls_tool
        els.append(bind_tool(ls_tool()))

        from ...minichain.lib.fs.tools.read import read_tool
        els.append(bind_tool(read_tool()))

    if tools_config.enable_todo_tools:
        from ...minichain.lib.todo.tools.read import todo_read_tool
        els.append(bind_tool(todo_read_tool()))

        from ...minichain.lib.todo.tools.write import todo_write_tool
        els.append(bind_tool(todo_write_tool()))

    if tools_config.enable_unsafe_tools_do_not_use_lol:
        from ...minichain.lib.bash import bash_tool
        els.append(bind_tool(bash_tool()))

        from ...minichain.lib.fs.tools.edit import edit_tool
        els.append(bind_tool(edit_tool()))

    if tools_config.enable_test_weather_tool:
        els.append(bind_tool(WEATHER_TOOL))

    #

    return inj.as_elements(*els)
