from omlish import lang

from ..descriptors import ModuleDescriptor
from .configs import SkillsConfig


with lang.auto_proxy_import(globals()):
    from . import inject as _inject


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='skills',
#     type='ModuleDescriptor',
# )
SKILLS_MODULE = ModuleDescriptor(
    name='skills',
    config_cls=SkillsConfig,
    binder=lambda cfg: _inject.bind_skills(cfg),
)
