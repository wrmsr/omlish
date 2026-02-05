import typing as ta

from ... import lang
from .registries import Registry
from .registries import RegistryItem
from .registries import RegistryView


ConfigT = ta.TypeVar('ConfigT', bound='Config')


##


class Config(RegistryItem, lang.Abstract):
    pass


Configs: ta.TypeAlias = RegistryView[Config]


##


ConfigRegistry: ta.TypeAlias = Registry[Config]

lang.static_check_issubclass[Configs](ConfigRegistry)


EMPTY_CONFIG_REGISTRY = ConfigRegistry().seal()
