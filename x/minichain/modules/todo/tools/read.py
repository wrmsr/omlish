import typing as ta

from omcore import contextual as cxl
from omcore import lang

from ....tools.execution.catalog import ToolCatalogEntry
from ....tools.execution.reflect import reflect_tool_catalog_entry
from ....tools.reflect import tool_spec_override
from ..context import TodoContext
from ..types import TodoItem


##


@tool_spec_override(
    desc="""
        Use this tool to read the current todo list for your current session. This tool should be used proactively and
        frequently to ensure that you are aware of the status of the current subtask list.

        You should make use of this tool often, especially in the following situations:
        - At the beginning of conversations to see what's pending.
        - Before starting new tasks to prioritize work.
        - When the user asks about previous tasks or plans.
        - Whenever you're uncertain about what to do next.
        - After completing tasks to update your understanding of remaining work.
        - After every few messages to ensure you're on track.

        Usage:
        - Returns a list of todo items in json format with their id, status, priority, and content.
        - Use this information to track progress and plan next steps.
    """,
)
@cxl.wrap()
def todo_read(
        *,
        ctx: TodoContext = cxl.param(),
) -> ta.Sequence[TodoItem]:
    return ctx.get_items() or []


@lang.cached_function
def todo_read_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(
        todo_read,
        marshal_output=True,
    )
