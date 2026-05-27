from omlish import contextual as cxl
from omlish import lang

from .....tools.execution.catalog import ToolCatalogEntry
from .....tools.execution.reflect import reflect_tool_catalog_entry
from ...context import FsContext
from .rendering import LsLinesRenderer
from .running import LsRunner


##


@cxl.wrap()
async def recursive_ls(
        base_path: str,
        *,
        ctx: FsContext = cxl.param(),
) -> str:
    """
    Recursively lists the directory contents of the given base path.

    Args:
        base_path: The path of the directory to list the contents of. Must be absolute.

    Returns:
        A formatted string of the recursive directory contents.
    """

    await ctx.check_requested_path(base_path)

    root = LsRunner().run(base_path)
    lines = LsLinesRenderer().render(root)
    return '\n'.join([
        '<dir>',
        *lines.lines,
        '</dir>',
    ])


@lang.cached_function
def recursive_ls_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(recursive_ls)
