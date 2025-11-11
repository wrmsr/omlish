from omlish import inject as inj

from ..injection import ToolSetBinder
from ..injection import bind_tool_context_provider_to_key
from ..injection import tool_catalog_entries
from .configs import TodoToolSetConfig


##


def bind_todo_tools(cfg: TodoToolSetConfig) -> inj.Elements:
    from ......minichain.lib.todo.context import TodoContext
    from ......minichain.lib.todo.tools.read import todo_read_tool
    from ......minichain.lib.todo.tools.write import todo_write_tool

    return inj.as_elements(
        tool_catalog_entries().bind_item_consts(
            todo_read_tool(),
            todo_write_tool(),
        ),

        inj.bind(TodoContext()),
        bind_tool_context_provider_to_key(TodoContext),
    )


##


TODO_TOOL_SET_BINDER = ToolSetBinder(TodoToolSetConfig, bind_todo_tools)
