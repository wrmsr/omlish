import abc
import typing as ta

from omlish import lang

from .collection import ToolPermissionRules
from .types import ToolPermissionRule
from .types import ToolPermissionTarget


##


class ToolPermissionsManager(lang.Abstract):
    @abc.abstractmethod
    def get_rules(self) -> ToolPermissionRules:
        raise NotImplementedError

    @abc.abstractmethod
    def add_rule(self, rule: ToolPermissionRule) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def match_target(self, target: ToolPermissionTarget) -> ToolPermissionRule | None:
        raise NotImplementedError


##


class SimpleToolPermissionsManager(ToolPermissionsManager):
    def __init__(self, rules: ta.Sequence[ToolPermissionRule] | None = None) -> None:
        super().__init__()

        self._rules = ToolPermissionRules(rules or ())

    def get_rules(self) -> ToolPermissionRules:
        return self._rules

    def add_rule(self, rule: ToolPermissionRule) -> None:
        self._rules = ToolPermissionRules([*self._rules, rule])

    def match_target(self, target: ToolPermissionTarget) -> ToolPermissionRule | None:
        for r in self._rules:
            if r.matcher.match(target):
                return r
        return None
