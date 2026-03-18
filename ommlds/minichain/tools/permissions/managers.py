import abc
import typing as ta

from omlish import lang

from .types import ToolPermissionRule
from .types import ToolPermissionTarget


##


class ToolPermissionsManager(lang.Abstract):
    @abc.abstractmethod
    def get_rules(self) -> ta.Sequence[ToolPermissionRule]:
        raise NotImplementedError

    @abc.abstractmethod
    def match(self, target: ToolPermissionTarget) -> ToolPermissionRule | None:
        raise NotImplementedError


class ListToolPermissionsManager(ToolPermissionsManager):
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
