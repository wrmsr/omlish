from omlish.configs.shadow import MangledFilesShadowConfigs
from omlish.configs.shadow import ShadowConfigs

from .paths import get_home_paths


##


def get_shadow_configs() -> ShadowConfigs:
    return MangledFilesShadowConfigs(
        get_home_paths().shadow_dir,
        create=True,
    )
