"""Obviously insanely unsafe at the moment, lol."""
import asyncio
import shutil

from omcore import check
from omcore import contextual as cxl
from omcore import lang

from ...tools.execution.catalog import ToolCatalogEntry
from ...tools.execution.reflect import reflect_tool_catalog_entry
from .context import BashContext


##


@cxl.wrap()
async def bash(
        bash_code: str,
        *,
        ctx: BashContext = cxl.param(),
) -> str:
    """
    Executes the given bash code in a new bash shell.

    Args:
        bash_code: The bash code to run.

    Returns:
        The stdout of the executed bash code.
    """

    await ctx.check_cmd_permitted(bash_code)

    proc = await asyncio.create_subprocess_exec(
        check.not_none(shutil.which('bash')),
        '-c',
        bash_code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(  # noqa
            proc.communicate(),
            timeout=10.0,
        )
    except TimeoutError:
        proc.kill()
        await proc.wait()
        raise

    return check.not_none(stdout).decode('utf-8')


@lang.cached_function
def bash_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(bash)
