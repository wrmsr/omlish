from ... import minichain as mc


##


WEATHER_TOOL_SPEC = mc.ToolSpec(
    'get_weather',
    [
        mc.ToolParam('location', 'string', desc='The location to get the weather for.'),
    ],
    desc='Gets the weather in the given location.',
)

WEATHER_TOOL = mc.Tool(WEATHER_TOOL_SPEC)
