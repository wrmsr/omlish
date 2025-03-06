# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import typing as ta

from ..lite.cached import cached_nullary
from ..lite.check import check


@dc.dataclass(frozen=True)
class StringMangler:
    escape: str
    escaped: ta.Sequence[str]

    @classmethod
    def of(cls, escape: str, escaped: ta.Iterable[str]) -> 'StringMangler':
        check.arg(len(escape) == 1)
        return StringMangler(escape, sorted(set(escaped) - {escape}))

    def __post_init__(self) -> None:
        check.non_empty_str(self.escape)
        check.arg(len(self.escape) == 1)
        check.not_in(self.escape, self.escaped)
        check.arg(len(set(self.escaped)) == len(self.escaped))

    @cached_nullary
    def replacements(self) -> ta.Sequence[ta.Tuple[str, str]]:
        return [(l, self.escape + str(i)) for i, l in enumerate([self.escape, *self.escaped])]

    def mangle(self, s: str) -> str:
        for l, r in self.replacements():
            s = s.replace(l, r)
        return s

    def unmangle(self, s: str) -> str:
        for l, r in reversed(self.replacements()):
            s = s.replace(r, l)
        return s
