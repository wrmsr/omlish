from omlish import lang
from omlish.formats import json

from ....tools.execution.catalog import ToolCatalogEntry
from ....tools.execution.reflect import reflect_tool_catalog_entry
from ....tools.reflect import tool_spec_override
from ..context import todo_tool_context


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
def execute_todo_read_tool() -> str:
    ctx = todo_tool_context()

    return json.dumps_compact(ctx.get_items() or [])


@lang.cached_function
def todo_read_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(execute_todo_read_tool)
