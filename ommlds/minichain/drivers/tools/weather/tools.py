from ....tools.execution.reflect import reflect_tool_catalog_entry


##


def get_weather(location: str) -> str:
    """
    Gets the weather in the given location.

    Args:
        location: The location to get the weather for.
    """

    return f'Foggy in {location}.'


WEATHER_TOOL = reflect_tool_catalog_entry(get_weather)
