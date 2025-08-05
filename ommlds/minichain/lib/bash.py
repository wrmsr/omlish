"""
Obviously insanely unsafe at the moment, lol.
"""
import shutil

from omlish import check
from omlish import lang
from omlish.subprocesses.sync import subprocesses

from ..tools.execution.catalog import ToolCatalogEntry
from ..tools.execution.reflect import reflect_tool_catalog_entry


##


def execute_bash_tool(
        bash_code: str,
) -> str:
    """
    Executes the given bash code in a new bash shell.

    Args:
        bash_code: The bash code to run.

    Returns:
        The stdout of the executed bash code.
    """

    res = subprocesses.run(
        check.not_none(shutil.which('bash')),
        '-c',
        bash_code,
        capture_output=True,
        timeout=10.,
    )

    return check.not_none(res.stdout).decode('utf-8')


@lang.cached_function
def bash_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(execute_bash_tool)
