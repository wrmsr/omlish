import glob
import re
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ... import _fieldhash as fh
from .types import ToolPermissionMatcher
from .types import ToolPermissionTarget


##


FsToolPermissionMode: ta.TypeAlias = ta.Literal['r', 'w']

FS_TOOL_PERMISSION_MODES: ta.Sequence[FsToolPermissionMode] = ('r', 'w')


@ta.final
@dc.dataclass(frozen=True)
class FsToolPermissionTarget(ToolPermissionTarget, lang.Final):
    path: str

    mode: FsToolPermissionMode

    @dc.validate
    def _validate_mode(self) -> bool:
        return self.mode in FS_TOOL_PERMISSION_MODES

    @lang.cached_function
    def _field_hash(self) -> fh.FieldHashValue:
        return fh.FieldHashObject('fs', (
            fh.FieldHashField('path', self.path),
            fh.FieldHashField('mode', self.mode),
        ))


@ta.final
@dc.dataclass(frozen=True)
class GlobFsToolPermissionMatcher(ToolPermissionMatcher, lang.Final):
    glob: str

    modes: ta.Container[FsToolPermissionMode] | None = dc.xfield(
        default=None,
    ) | dc.with_extra_field_params(
        coerce=lambda v: tuple(sorted({check.in_(m.lower(), FS_TOOL_PERMISSION_MODES) for m in v})) if v is not None else None,  # noqa
    ) | msh.with_field_options(
        omit_if=lang.is_none,
        marshal_as=ta.Sequence[FsToolPermissionMode] | None,
        unmarshal_as=ta.Sequence[FsToolPermissionMode] | None,
    )

    @lang.cached_function
    def _field_hash(self) -> fh.FieldHashValue:
        return fh.FieldHashObject('glob_fs', (
            fh.FieldHashField('glob', self.glob),
            fh.FieldHashField('modes', check.isinstance(self.modes, tuple) if self.modes is not None else None),
        ))

    @lang.cached_function
    def compiled_glob_pat(self) -> re.Pattern:
        return re.compile(glob.translate(self.glob, recursive=True, include_hidden=True))

    def match(self, target: ToolPermissionTarget) -> bool:
        if not isinstance(target, FsToolPermissionTarget):
            return False

        return (
            self.compiled_glob_pat().fullmatch(target.path) is not None and
            (self.modes is None or target.mode in self.modes)
        )
