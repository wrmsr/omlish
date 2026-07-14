import typing as ta

from omcore import dataclasses as dc
from omcore import inject as inj

from ..registries.globals import register_type
from .configs import ModuleConfig


ModuleConfigT = ta.TypeVar('ModuleConfigT', bound=ModuleConfig)


##


# @om-manifest $.minichain.registries.manifests.RegistryTypeManifest
@dc.dataclass(frozen=True, kw_only=True)
class ModuleDescriptor(ta.Generic[ModuleConfigT]):
    name: str
    config_cls: type[ModuleConfigT]
    binder: ta.Callable[[ModuleConfigT], inj.Elements]


register_type(ModuleDescriptor, module=__name__)
