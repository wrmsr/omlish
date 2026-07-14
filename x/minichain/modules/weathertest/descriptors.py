from omcore import lang

from ..descriptors import ModuleDescriptor
from .configs import WeatherTestConfig


with lang.auto_proxy_import(globals()):
    from . import inject as _inject


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='weather_test',
#     type='ModuleDescriptor',
# )
WEATHER_TEST_MODULE = ModuleDescriptor(
    name='weather_test',
    config_cls=WeatherTestConfig,
    binder=lambda cfg: _inject.bind_weather_test(cfg),
)
