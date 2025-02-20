from omlish.configs.shadow import MangledFilesShadowConfigs
from omlish.configs.shadow import ShadowConfigs

from .paths import get_shadow_dir


##


def get_shadow_configs() -> ShadowConfigs:
    return MangledFilesShadowConfigs(
        get_shadow_dir(),
        create=True,
    )
