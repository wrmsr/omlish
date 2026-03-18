# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - cascading?
 - caching?
 - purging?
 - wishlist: piecewise config parts, unmarshal, registered via manifests
"""
import abc
import os.path
import typing as ta

from ..lite.abstract import Abstract
from ..lite.check import check
from ..os.shadow import ShadowPaths
from .formats import DEFAULT_CONFIG_FILE_LOADER
from .formats import ConfigFileLoader


ShadowConfig = ta.Mapping[str, ta.Any]  # ta.TypeAlias


##


class ShadowConfigs(Abstract):
    @abc.abstractmethod
    def get_shadow_config(self, path: str, name: str) -> ta.Optional[ShadowConfig]:
        raise NotImplementedError


class FileShadowConfigs(ShadowConfigs, Abstract):
    @abc.abstractmethod
    def get_shadow_config_file_path(
            self,
            path: str,
            name: str,
            *,
            preferred_ext: ta.Optional[str] = None,
    ) -> ta.Optional[str]:
        raise NotImplementedError


##


class NopShadowConfigs(ShadowConfigs):
    def get_shadow_config(self, path: str, name: str) -> ta.Optional[ShadowConfig]:
        return None


##


class FileShadowConfigsImpl(FileShadowConfigs):
    def __init__(
            self,
            paths: ShadowPaths,
            subdir: ta.Optional[str] = None,
            *,
            loader: ta.Optional[ConfigFileLoader] = None,
            preferred_ext: ta.Optional[str] = None,
    ) -> None:  # noqa
        super().__init__()

        if loader is None:
            loader = DEFAULT_CONFIG_FILE_LOADER

        if preferred_ext is not None:
            check.arg(not preferred_ext.startswith('.'))
            check.non_empty_str(preferred_ext)
            check.in_(preferred_ext, loader.file_exts)

        self._paths = paths
        self._subdir = subdir
        self._loader = loader
        self._preferred_ext = preferred_ext

    def get_shadow_config_file_path(
            self,
            path: str,
            name: str,
            *,
            preferred_ext: ta.Optional[str] = None,
    ) -> ta.Optional[str]:
        check.non_empty_str(name)
        check.not_in(os.sep, name)

        shadow = self._paths.get_shadow_path(path)
        if (sd := self._subdir):
            shadow = os.path.join(shadow, sd)

        hits: ta.List[str] = []
        for loader_ext in self._loader.file_exts:
            cur = os.path.join(shadow, f'{name}.{loader_ext}')
            if os.path.exists(cur):
                check.state(os.path.isfile(cur))
                hits.append(cur)

        if hits:
            return check.single(hits)
        elif (px := (preferred_ext if preferred_ext is not None else self._preferred_ext)) is not None:
            return os.path.join(shadow, f'{name}.{px}')
        else:
            return None

    def get_shadow_config(self, path: str, name: str) -> ta.Optional[ShadowConfig]:
        if (file_path := self.get_shadow_config_file_path(path, name)) is None:
            return None

        if not os.path.exists(file_path):
            return None

        return self._loader.load_file(file_path).as_map()
