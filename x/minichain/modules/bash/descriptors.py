from omcore import lang

from ..descriptors import ModuleDescriptor
from .configs import BashConfig


with lang.auto_proxy_import(globals()):
    from . import inject as _inject


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='bash',
#     type='ModuleDescriptor',
# )
BASH_MODULE = ModuleDescriptor(
    name='bash',
    config_cls=BashConfig,
    binder=lambda cfg: _inject.bind_bash(cfg),
)
