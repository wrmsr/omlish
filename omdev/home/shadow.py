"""
TODO:
 - <hostname>/ subdir?
"""
from omcore.configs.shadow import FileShadowConfigs
from omcore.configs.shadow import FileShadowConfigsImpl
from omcore.configs.shadow import ShadowConfigs
from omcore.lite.check import check
from omcore.os.shadow import ManglingShadowPaths
from omcore.os.shadow import ShadowPaths

from .paths import HomePaths
from .paths import get_home_paths


##


def get_shadow_paths() -> ShadowPaths:
    return ManglingShadowPaths(get_home_paths().shadow_dir)


def get_shadow_configs() -> ShadowConfigs:
    return FileShadowConfigsImpl(get_shadow_paths(), HomePaths.config_subdir)


def get_file_shadow_configs() -> FileShadowConfigs:
    return check.isinstance(get_shadow_configs(), FileShadowConfigs)
