from omcore import lang

from ..descriptors import ModuleDescriptor
from .configs import WebConfig


with lang.auto_proxy_import(globals()):
    from . import inject as _inject


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='web',
#     type='ModuleDescriptor',
# )
WEB_MODULE = ModuleDescriptor(
    name='web',
    config_cls=WebConfig,
    binder=lambda cfg: _inject.bind_web(cfg),
)
