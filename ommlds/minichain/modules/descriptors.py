from omlish import dataclasses as dc

from ..registries.globals import register_type
from .configs import ModuleConfig


##


# @omlish-manifest $.minichain.registries.manifests.RegistryTypeManifest
@dc.dataclass(frozen=True, kw_only=True)
class ModuleDescriptor:
    name: str
    config_cls: type[ModuleConfig]


register_type(ModuleDescriptor, module=__name__)
