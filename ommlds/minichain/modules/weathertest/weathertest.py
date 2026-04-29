from omlish import lang

from ...tools.execution.catalog import ToolCatalogEntry
from ...tools.execution.reflect import reflect_tool_catalog_entry


##


def weather(location: str) -> str:
    """
    Gets the weather in the given location.

    Args:
        location: The location to get the weather for.
    """

    return f'Foggy in {location}.'


@lang.cached_function
def weather_tool() -> ToolCatalogEntry:
    return reflect_tool_catalog_entry(weather)
