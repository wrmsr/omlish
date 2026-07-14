from omlish import lang

from ..descriptors import ModuleDescriptor
from .configs import CodeConfig


with lang.auto_proxy_import(globals()):
    from . import inject as _inject


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='code',
#     type='ModuleDescriptor',
# )
CODE_MODULE = ModuleDescriptor(
    name='code',
    config_cls=CodeConfig,
    binder=lambda cfg: _inject.bind_code(cfg),
)
