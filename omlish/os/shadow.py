# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import os.path

from ..lite.abstract import Abstract
from .mangle import mangle_path


##


class ShadowPaths(Abstract):
    @abc.abstractmethod
    def get_shadow_path(self, path: str) -> str:
        raise NotImplementedError


class ManglingShadowPaths(ShadowPaths):
    def __init__(
            self,
            root_path: str,
    ) -> None:  # noqa
        super().__init__()

        self._root_path = root_path

    def get_shadow_path(self, path: str) -> str:
        mangled = mangle_path(os.path.abspath(path))
        return os.path.abspath(os.path.join(self._root_path, mangled))
