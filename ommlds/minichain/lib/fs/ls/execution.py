from omlish import lang

from ....tools.execution.catalog import ToolCatalogEntry
from ....tools.execution.reflect import reflect_tool_catalog_entry
from .rendering import LsLinesRenderer
from .running import LsRunner


##


def execute_ls_tool(
        base_path: str,
) -> str:
    """
    Recursively lists the directory contents of the given base path.

    Args:
        base_path: The path of the directory to list the contents of.

    Returns:
        A formatted string of the recursive directory contents.
    """

    root = LsRunner().run(base_path)
    lines = LsLinesRenderer().render(root)
    return '\n'.join(lines.lines)


@lang.cached_function
def ls_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(execute_ls_tool)
