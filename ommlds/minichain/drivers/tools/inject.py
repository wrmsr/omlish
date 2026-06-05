from omlish import inject as inj

from ...tools.execution.catalog import ToolCatalog
from ...tools.execution.errorhandling import ErrorHandlingToolUseExecutor
from ...tools.execution.eventemit import EventEmittingToolUseExecutor
from ...tools.execution.execution import ToolUseExecutor
from ...tools.execution.execution import ToolUseExecutorImpl
from ...tools.execution.injection import bind_tool_context_provider_to_key
from ...tools.execution.injection import tool_catalog_entries
from ...tools.execution.injection import tool_context_providers
from ...tools.execution.metadataadd import MetadataAddingToolUseExecutor
from ...tools.execution.permissions import ToolPermissionDecider
from ..configs import ToolsConfig
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

    # Outermost, so emitted events carry the final (metadata-stamped) results - the same values that get persisted.
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
    ])

    #

    return inj.as_elements(*els)
