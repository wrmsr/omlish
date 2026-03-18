import re
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .types import ToolPermissionMatcher
from .types import ToolPermissionTarget


##


@dc.dataclass(frozen=True)
class UrlToolPermissionTarget(ToolPermissionTarget, lang.Final):
    url: str

    _: dc.KW_ONLY

    method: str | None = None


@dc.dataclass(frozen=True)
class RegexUrlToolPermissionMatcher(ToolPermissionMatcher, lang.Final):
    pat: str

    _: dc.KW_ONLY

    method: ta.AbstractSet[str] | None = None

    @lang.cached_function
    def compiled_pat(self) -> re.Pattern:
        return re.compile(self.pat)

    def match(self, target: ToolPermissionTarget) -> bool:
        if not isinstance(target, UrlToolPermissionTarget):
            return False

        return (
            self.compiled_pat().fullmatch(target.url) is not None and
            (self.method is None or (target.method is not None and target.method in self.method))
        )
