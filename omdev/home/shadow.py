from omlish.configs.shadow import FileShadowConfigs
from omlish.configs.shadow import FileShadowConfigsImpl
from omlish.configs.shadow import ShadowConfigs
from omlish.lite.check import check
from omlish.os.shadow import ManglingShadowPaths
from omlish.os.shadow import ShadowPaths

from .paths import HomePaths
from .paths import get_home_paths


##


def get_shadow_paths() -> ShadowPaths:
    return ManglingShadowPaths(get_home_paths().shadow_dir)


def get_shadow_configs() -> ShadowConfigs:
    return FileShadowConfigsImpl(get_shadow_paths(), HomePaths.config_subdir)


def get_file_shadow_configs() -> FileShadowConfigs:
    return check.isinstance(get_shadow_configs(), FileShadowConfigs)
