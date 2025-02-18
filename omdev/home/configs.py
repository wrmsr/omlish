import os.path

from omlish.configs.shadow import MangledFilesShadowConfigs
from omlish.configs.shadow import ShadowConfigs

from .paths import get_home_dir


def get_shadow_configs() -> ShadowConfigs:
    return MangledFilesShadowConfigs(
        os.path.join(get_home_dir(), 'shadow'),
        create=True,
    )
