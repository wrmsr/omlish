from omlish import check
from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from .injection import tool_catalog_entries
from .injection import tool_context_providers


with lang.auto_proxy_import(globals()):
    from . import confirmation as _confirmation
    from . import execution as _execution
    from . import rendering as _rendering


##


def bind_tools(
        *,
        silent: bool = False,
        interactive: bool = False,
        dangerous_no_confirmation: bool = False,

        enable_weather_tools: bool = True,
        enable_todo_tools: bool = True,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(inj.bind(mc.ToolCatalog, singleton=True))

    #

    els.append(tool_catalog_entries().bind_items_provider(singleton=True))

    if enable_weather_tools:
        from ....tools.weather import WEATHER_TOOL
        els.append(tool_catalog_entries().bind_item_consts(WEATHER_TOOL))

    if enable_todo_tools:
        from .....minichain.lib.todo.tools.read import todo_read_tool
        from .....minichain.lib.todo.tools.write import todo_write_tool

        els.append(tool_catalog_entries().bind_item_consts(
            todo_read_tool(),
            todo_write_tool(),
        ))

        from .....minichain.lib.todo.context import TodoContext
        els.extend([
            inj.bind(TodoContext()),
            tool_context_providers().bind_item(to_fn=lang.typed_lambda(tdc=TodoContext)(
                lambda tdc: _execution.ToolContextProvider(lambda: [tdc]),
            ), singleton=True),
        ])

    #

    exec_stack = inj.wrapper_binder_helper(_execution.ToolUseExecutor)

    els.append(exec_stack.push_bind(to_ctor=_execution.ToolUseExecutorImpl, singleton=True))

    if not silent:
        els.append(exec_stack.push_bind(to_ctor=_rendering.ResultRenderingToolUseExecutor, singleton=True))

        if dangerous_no_confirmation:
            els.append(exec_stack.push_bind(to_ctor=_rendering.ArgsRenderingToolUseExecutor, singleton=True))

    els.extend([
        inj.bind(_execution.ToolUseExecutor, to_key=exec_stack.top),
    ])

    #

    if not dangerous_no_confirmation:
        check.state(interactive, 'Interactive is required for tool confirmation')
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
