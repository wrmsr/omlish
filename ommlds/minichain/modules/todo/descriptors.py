from omlish import lang

from ..descriptors import ModuleDescriptor
from .configs import TodoConfig


with lang.auto_proxy_import(globals()):
    from . import inject as _inject


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='todo',
#     type='ModuleDescriptor',
# )
TODO_MODULE = ModuleDescriptor(
    name='todo',
    config_cls=TodoConfig,
    binder=lambda cfg: _inject.bind_todo(cfg),
)
