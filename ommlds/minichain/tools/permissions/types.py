import abc
import enum
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from . import _fieldhash as fh


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


@ta.final
@dc.dataclass(frozen=True)
class ToolPermissionRules(fh.FieldHashable, lang.Final):
    rules: ta.Sequence[ToolPermissionRule] = dc.xfield(coerce=tuple)

    def _field_hash(self) -> fh.FieldHashValue:
        return fh.FieldHashObject('rules', (
            fh.FieldHashField('rules', check.isinstance(self.rules, tuple)),
        ))


##


class ToolPermissions(lang.Abstract):
    @abc.abstractmethod
    def get_rules(self) -> ta.Sequence[ToolPermissionRule]:
        raise NotImplementedError

    @abc.abstractmethod
    def match(self, target: ToolPermissionTarget) -> ToolPermissionRule | None:
        raise NotImplementedError


class ListToolPermissions(ToolPermissions):
    def __init__(self, rules: ta.Sequence[ToolPermissionRule] | None = None) -> None:
        super().__init__()

        self._rules = list(rules or ())

    def get_rules(self) -> ta.Sequence[ToolPermissionRule]:
        return self._rules

    def match(self, target: ToolPermissionTarget) -> ToolPermissionRule | None:
        for r in self._rules:
            if r.matcher.match(target):
                return r
        return None
