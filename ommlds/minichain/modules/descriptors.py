import typing as ta

from omlish import dataclasses as dc
from omlish import inject as inj

from ..registries.globals import register_type
from .configs import ModuleConfig


ModuleConfigT = ta.TypeVar('ModuleConfigT', bound=ModuleConfig)


##


# @omlish-manifest $.minichain.registries.manifests.RegistryTypeManifest
@dc.dataclass(frozen=True, kw_only=True)
class ModuleDescriptor(ta.Generic[ModuleConfigT]):
    name: str
    config_cls: type[ModuleConfigT]
    binder: ta.Callable[[ModuleConfigT], inj.Elements]


register_type(ModuleDescriptor, module=__name__)
