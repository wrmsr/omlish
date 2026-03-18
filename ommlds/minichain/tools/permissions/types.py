import abc
import enum
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ... import _fieldhash as fh


##


class ToolPermissionState(enum.Enum):
    DENY = enum.auto()
    ASK = enum.auto()
    ALLOW = enum.auto()


##


@dc.dataclass(frozen=True)
class ToolPermissionTarget(fh.FieldHashable, lang.Abstract, lang.PackageSealed):
    pass


class ToolPermissionMatcher(fh.FieldHashable, lang.Abstract):
    @abc.abstractmethod
    def match(self, target: ToolPermissionTarget) -> bool:
        raise NotImplementedError


##


@ta.final
@dc.dataclass(frozen=True)
class ToolPermissionRule(fh.FieldHashable, lang.Final):
    matcher: ToolPermissionMatcher
    result: ToolPermissionState

    def _field_hash(self) -> fh.FieldHashValue:
        return fh.FieldHashObject('rule', (
            fh.FieldHashField('matcher', self.matcher),
            fh.FieldHashField('result', self.result.name),
        ))
