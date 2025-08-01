from ... import minichain as mc


##


def _get_weather(location: str) -> str:
    return f'Foggy in {location}.'


_WEATHER_TOOL_SPEC = mc.ToolSpec(
    'get_weather',
    params=[
        mc.ToolParam(
            'location',
            type=mc.ToolDtype.of(str),
            desc='The location to get the weather for.',
        ),
    ],
    desc='Gets the weather in the given location.',
)


WEATHER_TOOL = mc.ToolCatalogEntry(
    _WEATHER_TOOL_SPEC,
    mc.ToolFn(
        _get_weather,
        mc.ToolFn.KwargsInput(),
        mc.ToolFn.RawStringOutput(),
    ),
)
