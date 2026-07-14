import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ... import _fieldhash as fh
from .types import ToolPermissionMatcher
from .types import ToolPermissionTarget


##


@ta.final
@dc.dataclass(frozen=True)
class BashToolPermissionTarget(ToolPermissionTarget, lang.Final):
    cmd: str

    @lang.cached_function
    def _field_hash(self) -> fh.FieldHashValue:
        return fh.FieldHashObject('bash', (
            fh.FieldHashField('cmd', self.cmd),
        ))


@ta.final
@dc.dataclass(frozen=True)
class BashToolPermissionMatcher(ToolPermissionMatcher, lang.Final):
    @lang.cached_function
    def _field_hash(self) -> fh.FieldHashValue:
        return fh.FieldHashObject('bash', ())

    def match(self, target: ToolPermissionTarget) -> bool:
        return isinstance(target, BashToolPermissionTarget)
