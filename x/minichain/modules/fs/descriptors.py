from omlish import lang

from ..descriptors import ModuleDescriptor
from .configs import FsConfig


with lang.auto_proxy_import(globals()):
    from . import inject as _inject


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='fs',
#     type='ModuleDescriptor',
# )
FS_MODULE = ModuleDescriptor(
    name='fs',
    config_cls=FsConfig,
    binder=lambda cfg: _inject.bind_fs(cfg),
)
