import io
import os

from omlish import lang

from ....tools.execution.catalog import ToolCatalogEntry
from ....tools.execution.reflect import reflect_tool_catalog_entry
from ..context import tool_fs_context


##


def execute_ls_tool(
        dir_path: str,
) -> str:
    """
    Lists the contents of the specified dir.

    Args:
        dir_path: The dir to list the contents of. Must be an absolute path.
    """

    ctx = tool_fs_context()
    ctx.check_stat_dir(dir_path)

    out = io.StringIO()
    out.write('<dir>\n')
    for e in sorted(os.scandir(dir_path), key=lambda e: e.name):  # noqa
        out.write(f'{e.name}{"/" if e.is_dir() else ""}\n')
    out.write('</dir>\n')

    return out.getvalue()


@lang.cached_function
def ls_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(execute_ls_tool)
