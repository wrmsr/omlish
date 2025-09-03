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
from ..os.mangle import mangle_path
from .formats import DEFAULT_CONFIG_LOADERS
from .formats import ConfigLoader


ShadowConfig = ta.Mapping[str, ta.Any]  # ta.TypeAlias


##


class ShadowConfigs(Abstract):
    @abc.abstractmethod
    def get_shadow_config(self, path: str) -> ta.Optional[ShadowConfig]:
        raise NotImplementedError


class FileShadowConfigs(ShadowConfigs, Abstract):
    @abc.abstractmethod
    def get_shadow_config_file_path(self, path: str) -> str:
        raise NotImplementedError


##


class NopShadowConfigs(ShadowConfigs):
    def get_shadow_config(self, path: str) -> ta.Optional[ShadowConfig]:
        return None


##


class MangledFilesShadowConfigs(FileShadowConfigs):
    def __init__(
            self,
            path: str,
            *,
            create: bool = False,
            ext: str = 'yml',
            loader: ta.Optional[ConfigLoader] = None,
    ) -> None:  # noqa
        super().__init__()

        check.arg(not ext.startswith('.'))
        check.non_empty_str(ext)

        if loader is None:
            for dl in DEFAULT_CONFIG_LOADERS:
                if dl.match_file(f'.{ext}'):
                    loader = dl
                    break
            else:
                raise KeyError(ext)

        self._path = path
        self._create = create
        self._ext = ext
        self._loader = loader

    def get_shadow_config_file_path(self, path: str) -> str:
        mangled = '.'.join([mangle_path(os.path.abspath(path)), self._ext])
        return os.path.abspath(os.path.join(self._path, mangled))

    def get_shadow_config(self, path: str) -> ta.Optional[ShadowConfig]:
        file_path = self.get_shadow_config_file_path(path)

        if self._create:
            os.makedirs(self._path, exist_ok=True)

        try:
            with open(file_path) as f:
                content = f.read()
        except FileNotFoundError:
            return None

        return self._loader.load_str(content).as_map()
