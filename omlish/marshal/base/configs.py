import dataclasses as dc
import typing as ta

from ... import lang
from .registries import Registry
from .registries import RegistryItem


##


class Config(RegistryItem, lang.Abstract):
    pass


ConfigRegistry: ta.TypeAlias = Registry[Config]


EMPTY_CONFIG_REGISTRY = ConfigRegistry().seal()


##


@dc.dataclass(frozen=True, eq=False)
class ModuleImport(Config, lang.Final):
    name: str
    package: str | None = None
