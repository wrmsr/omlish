import inspect
import os
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from .configs import ToolsConfig
from .injection import bind_tool_context_provider_to_key
from .injection import tool_catalog_entries
from .injection import tool_context_providers


with lang.auto_proxy_import(globals()):
    from . import confirmation as _confirmation
    from . import execution as _execution
    from . import rendering as _rendering


ToolSetConfigT = ta.TypeVar('ToolSetConfigT', bound='ToolSetConfig')


##


@dc.dataclass(frozen=True, kw_only=True)
class ToolSetConfig(lang.Abstract):
    pass


##


_TOOL_SET_BINDERS: dict[type[ToolSetConfig], ta.Callable[[ta.Any], inj.Elements]] = {}


def _tool_set_binder(fn: ta.Callable[[ToolSetConfigT], inj.Elements]) -> ta.Callable[[ToolSetConfigT], inj.Elements]:
    [param] = inspect.signature(fn).parameters.values()
    cfg_cls = check.issubclass(param.annotation, ToolSetConfig)
    check.not_in(cfg_cls, _TOOL_SET_BINDERS)
    _TOOL_SET_BINDERS[cfg_cls] = fn
    return fn


##


@dc.dataclass(frozen=True, kw_only=True)
class WeatherToolSetConfig(ToolSetConfig, lang.Final):
    pass


@_tool_set_binder
def _bind_weather_tool_set(cfg:WeatherToolSetConfig) -> inj.Elements:
    from .weather import WEATHER_TOOL

    return inj.as_elements(
        tool_catalog_entries().bind_item_consts(WEATHER_TOOL),
    )


#


@dc.dataclass(frozen=True, kw_only=True)
class TodoToolSetConfig(ToolSetConfig, lang.Final):
    pass


@_tool_set_binder
def _bind_todo_tools(cfg: TodoToolSetConfig) -> inj.Elements:
    from .....minichain.lib.todo.context import TodoContext
    from .....minichain.lib.todo.tools.read import todo_read_tool
    from .....minichain.lib.todo.tools.write import todo_write_tool

    return inj.as_elements(
        tool_catalog_entries().bind_item_consts(
            todo_read_tool(),
            todo_write_tool(),
        ),

        inj.bind(TodoContext()),
        bind_tool_context_provider_to_key(TodoContext),
    )


#


@dc.dataclass(frozen=True, kw_only=True)
class FsToolSetConfig(ToolSetConfig, lang.Final):
    pass


@_tool_set_binder
def _bind_fs_tools(cfg: FsToolSetConfig) -> inj.Elements:
    from .....minichain.lib.fs.context import FsContext
    from .....minichain.lib.fs.tools.ls import ls_tool
    from .....minichain.lib.fs.tools.read import read_tool

    return inj.as_elements(
        tool_catalog_entries().bind_item_consts(
            ls_tool(),
            read_tool(),
        ),

        inj.bind(FsContext(
            root_dir=os.getcwd(),
        )),
        bind_tool_context_provider_to_key(FsContext),
    )


#


# if tools_config.enable_unsafe_tools_do_not_use_lol:
#     from ...minichain.lib.bash import bash_tool
#     els.append(bind_tool(bash_tool()))
#
#     from ...minichain.lib.fs.tools.edit import edit_tool
#     els.append(bind_tool(edit_tool()))


##


def bind_tools(cfg: ToolsConfig = ToolsConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(inj.bind(mc.ToolCatalog, singleton=True))

    #

    els.append(tool_catalog_entries().bind_items_provider(singleton=True))

    for etn in check.not_isinstance(cfg.enabled_tools or [], str):
        ts_cfg = {  # FIXME: placeholder obviously lol
            'weather': WeatherToolSetConfig,
            'todo': TodoToolSetConfig,
            'fs': FsToolSetConfig,
        }[etn]()

        els.append(_TOOL_SET_BINDERS[type(ts_cfg)](ts_cfg))

    #

    exec_stack = inj.wrapper_binder_helper(_execution.ToolUseExecutor)

    els.append(exec_stack.push_bind(to_ctor=_execution.ToolUseExecutorImpl, singleton=True))

    if not cfg.silent:
        els.append(exec_stack.push_bind(to_ctor=_rendering.ResultRenderingToolUseExecutor, singleton=True))

        if cfg.dangerous_no_confirmation:
            els.append(exec_stack.push_bind(to_ctor=_rendering.ArgsRenderingToolUseExecutor, singleton=True))

    els.extend([
        inj.bind(_execution.ToolUseExecutor, to_key=exec_stack.top),
    ])

    #

    if not cfg.dangerous_no_confirmation:
        els.append(inj.bind(_confirmation.ToolExecutionConfirmation, to_ctor=_confirmation.InteractiveToolExecutionConfirmation, singleton=True))  # noqa

    #

    els.extend([
        tool_context_providers().bind_items_provider(singleton=True),

        inj.bind(_execution.ToolContextProvider, to_fn=lang.typed_lambda(tcps=_execution.ToolContextProviders)(
            lambda tcps: _execution.ToolContextProvider(lambda: [tc for tcp in tcps for tc in tcp()]),
        ), singleton=True),
    ])

    #

    return inj.as_elements(*els)
