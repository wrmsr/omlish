from ..descriptors import ModuleDescriptor
from .configs import BashConfig


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='bash',
#     type='ModuleDescriptor',
# )
BASH_MODULE = ModuleDescriptor(
    name='bash',
    config_cls=BashConfig,
)
