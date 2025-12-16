from omlish import check
from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from .configs import ToolsConfig
from .injection import ToolSetBinder
from .injection import tool_catalog_entries
from .injection import tool_context_providers


with lang.auto_proxy_import(globals()):
    from . import confirmation as _confirmation
    from . import execution as _execution
    from . import rendering as _rendering


##


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
        from .fs.inject import FS_TOOL_SET_BINDER
        from .todo.inject import TODO_TOOL_SET_BINDER
        from .weather.inject import WEATHER_TOOL_SET_BINDER
        ts_binder: ToolSetBinder = {  # type: ignore[assignment]  # FIXME: placeholder obviously lol
            'fs': FS_TOOL_SET_BINDER,
            'todo': TODO_TOOL_SET_BINDER,
            'weather': WEATHER_TOOL_SET_BINDER,
        }[etn]

        els.append(ts_binder.fn(ts_binder.cfg_cls()))

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
