import fnmatch
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .types import ToolPermissionMatcher
from .types import ToolPermissionTarget


FsToolPermissionMode: ta.TypeAlias = ta.Literal['r', 'w']


##


@dc.dataclass(frozen=True)
class FsToolPermissionTarget(ToolPermissionTarget, lang.Final):
    path: str

    mode: FsToolPermissionMode


@dc.dataclass(frozen=True)
class GlobFsToolPermissionMatcher(ToolPermissionMatcher, lang.Final):
    glob: str

    mode: ta.Container[FsToolPermissionMode] | None = None

    def match(self, target: ToolPermissionTarget) -> bool:
        if not isinstance(target, FsToolPermissionTarget):
            return False

        return (
            fnmatch.fnmatch(target.path, self.glob) and
            (self.mode is None or target.mode in self.mode)
        )
