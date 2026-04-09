from omlish import inject as inj

from ...tools.execution.catalog import ToolCatalog
from ...tools.execution.permissions import ToolPermissionDecider
from ..configs import ToolsConfig
from .errorhandling import ErrorHandlingToolUseExecutor
from .eventemit import EventEmittingToolUseExecutor
from .execution import ToolContextProvider
from .execution import ToolContextProviders
from .execution import ToolUseExecutor
from .execution import ToolUseExecutorImpl
from .injection import bind_tool_context_provider_to_key
from .injection import tool_catalog_entries
from .injection import tool_context_providers
from .metadata import MetadataAddingToolUseExecutor
from .permissions import StandardToolPermissionDecider


##


def bind_tools(cfg: ToolsConfig = ToolsConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(inj.bind(ToolCatalog, singleton=True))

    #

    els.append(tool_catalog_entries().bind_items_provider(singleton=True))

    #

    exec_stack = inj.wrapper_binder_helper(ToolUseExecutor)

    els.append(exec_stack.push_bind(to_ctor=ToolUseExecutorImpl, singleton=True))

    els.append(exec_stack.push_bind(to_ctor=ErrorHandlingToolUseExecutor, singleton=True))

    els.append(exec_stack.push_bind(to_ctor=MetadataAddingToolUseExecutor, singleton=True))

    els.append(exec_stack.push_bind(to_ctor=EventEmittingToolUseExecutor, singleton=True))

    els.extend([
        inj.bind(ToolUseExecutor, to_key=exec_stack.top),
    ])

    #

    els.extend([
        inj.bind(StandardToolPermissionDecider, singleton=True),
        inj.bind(ToolPermissionDecider, to_key=StandardToolPermissionDecider),
        bind_tool_context_provider_to_key(ToolPermissionDecider),
    ])

    #

    els.extend([
        tool_context_providers().bind_items_provider(singleton=True),

        inj.bind(ToolContextProvider, to_fn=inj.target(tcps=ToolContextProviders)(
            lambda tcps: ToolContextProvider(lambda: [tc for tcp in tcps for tc in tcp()]),
        ), singleton=True),
    ])

    #

    return inj.as_elements(*els)
