import abc
import enum
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


class ToolPermissionState(enum.Enum):
    DENY = enum.auto()
    ASK = enum.auto()
    ALLOW = enum.auto()


##


@dc.dataclass(frozen=True)
class ToolPermissionTarget(lang.Abstract, lang.PackageSealed):
    pass


class ToolPermissionMatcher(lang.Abstract):
    @abc.abstractmethod
    def match(self, target: ToolPermissionTarget) -> bool:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class ToolPermissionRule(lang.Final):
    matcher: ToolPermissionMatcher
    result: ToolPermissionState


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
