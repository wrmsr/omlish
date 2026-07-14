from omlish import inject as inj
from omlish import lang

from ...tools.execution.injection import tool_catalog_entries
from .configs import WeatherTestConfig


with lang.auto_proxy_import(globals()):
    from . import weathertest as _weathertest


##


def bind_weather_test(cfg: WeatherTestConfig = WeatherTestConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(
        tool_catalog_entries().bind_item_consts(
            _weathertest.weather_tool(),
        ),
    )

    #

    return inj.as_elements(*els)
