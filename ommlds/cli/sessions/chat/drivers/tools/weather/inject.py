from omlish import inject as inj

from ..injection import ToolSetBinder
from ..injection import tool_catalog_entries
from .configs import WeatherToolSetConfig


##


def bind_weather_tools(cfg: WeatherToolSetConfig) -> inj.Elements:
    from .tools import WEATHER_TOOL

    return inj.as_elements(
        tool_catalog_entries().bind_item_consts(WEATHER_TOOL),
    )


##


WEATHER_TOOL_SET_BINDER = ToolSetBinder(WeatherToolSetConfig, bind_weather_tools)
