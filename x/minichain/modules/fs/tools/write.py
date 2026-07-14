from omcore import contextual as cxl
from omcore import lang

from ....tools.execution.catalog import ToolCatalogEntry
from ....tools.execution.reflect import reflect_tool_catalog_entry
from ..context import FsContext


##


@cxl.wrap()
async def write_file(
        *,
        file_path: str,
        contents: str,
        overwrite: bool = False,

        ctx: FsContext = cxl.param(),
) -> str:
    """
    Writes a new file at the given absolute path with the given contents.

    If `overwrite` is not true, then the file must not already exist. If `overwrite` is true, then any file at the given
    path will be overwritten.

    Args:
        file_path: The path of the file to write. Must be an absolute path.
        contents: The contents of the file to write.
        overwrite: Whether or not to overwrite existing files. Defaults to False.
    """

    if overwrite:
        await ctx.check_writes_permitted(file_path)
    else:
        await ctx.check_not_exists(file_path, write=True)

    with open(file_path, 'w') as f:  # noqa
        f.write(contents)

    return 'The file has been written successfully.'


@lang.cached_function
def write_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(write_file)
