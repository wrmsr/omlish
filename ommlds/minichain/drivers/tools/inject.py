from omlish import check
from omlish import inject as inj
from omlish import lang

from ...tools.execution.catalog import ToolCatalog
from ..configs import ToolsConfig
from .errorhandling import ErrorHandlingToolUseExecutor
from .events import EventEmittingToolUseExecutor
from .execution import ToolContextProvider
from .execution import ToolContextProviders
from .execution import ToolUseExecutor
from .execution import ToolUseExecutorImpl
from .injection import ToolSetBinder
from .injection import tool_catalog_entries
from .injection import tool_context_providers


##


def bind_tools(cfg: ToolsConfig = ToolsConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(inj.bind(ToolCatalog, singleton=True))

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

    exec_stack = inj.wrapper_binder_helper(ToolUseExecutor)

    els.append(exec_stack.push_bind(to_ctor=ToolUseExecutorImpl, singleton=True))

    els.append(exec_stack.push_bind(to_ctor=ErrorHandlingToolUseExecutor, singleton=True))

    els.append(exec_stack.push_bind(to_ctor=EventEmittingToolUseExecutor, singleton=True))

    els.extend([
        inj.bind(ToolUseExecutor, to_key=exec_stack.top),
    ])

    #

    els.extend([
        tool_context_providers().bind_items_provider(singleton=True),

        inj.bind(ToolContextProvider, to_fn=lang.typed_lambda(tcps=ToolContextProviders)(
            lambda tcps: ToolContextProvider(lambda: [tc for tcp in tcps for tc in tcp()]),
        ), singleton=True),
    ])

    #

    return inj.as_elements(*els)
