from omlish import lang

from .....tools.execution.catalog import ToolCatalogEntry
from .....tools.execution.reflect import reflect_tool_catalog_entry
from ...context import tool_fs_context
from .rendering import LsLinesRenderer
from .running import LsRunner


##


def execute_recursive_ls_tool(
        base_path: str,
) -> str:
    """
    Recursively lists the directory contents of the given base path.

    Args:
        base_path: The path of the directory to list the contents of. Must be absolute.

    Returns:
        A formatted string of the recursive directory contents.
    """

    ft_ctx = tool_fs_context()
    ft_ctx.check_requested_path(base_path)

    root = LsRunner().run(base_path)
    lines = LsLinesRenderer().render(root)
    return '\n'.join([
        '<dir>',
        *lines.lines,
        '</dir>',
    ])


@lang.cached_function
def recursive_ls_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(execute_recursive_ls_tool)
