import typing as ta

from ... import lang
from .registries import Registry
from .registries import RegistryItem


##


class Config(RegistryItem, lang.Abstract):
    pass


ConfigRegistry: ta.TypeAlias = Registry[Config]


EMPTY_CONFIG_REGISTRY = ConfigRegistry().seal()
