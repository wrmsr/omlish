from omlish import lang

from .....minichain.tools.execution.catalog import ToolCatalogEntry
from .....minichain.tools.execution.reflect import reflect_tool_catalog_entry


##


async def execute_skill_tool(
        name: str,
        args: str | None = None,
) -> str:
    """
    Execute a skill.

    Args:
        name: The skill name.
        args: Optional arguments for the skill.
    """

    raise NotImplementedError


@lang.cached_function
def skill_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(execute_skill_tool)
