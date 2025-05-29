import dataclasses as dc
import typing as ta

from ... import minichain as mc


##


@dc.dataclass(frozen=True)
class Tool:
    spec: mc.ToolSpec
    fn: ta.Callable


ToolMap = ta.NewType('ToolMap', ta.Mapping[str, Tool])


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


WEATHER_TOOL = Tool(
    _WEATHER_TOOL_SPEC,
    _get_weather,
)
