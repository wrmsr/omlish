# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import re
import typing as ta

from ..lite.cached import cached_nullary
from ..lite.check import check


##


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

    #

    @cached_nullary
    def replaced(self) -> ta.Tuple[str, ...]:
        return (self.escape, *self.escaped)

    @cached_nullary
    def replaced_set(self) -> ta.FrozenSet[str]:
        return frozenset(self.replaced())

    @cached_nullary
    def replaced_indexes(self) -> ta.Mapping[str, int]:
        return {s: i for i, s in enumerate(self.replaced())}

    @cached_nullary
    def replaced_pat(self) -> re.Pattern:
        return re.compile('|'.join(re.escape(k) for k in self.replaced()))

    #

    @cached_nullary
    def replacement_pad(self) -> int:
        return len('%x' % (len(self.replaced()),))  # noqa

    @cached_nullary
    def replacements(self) -> ta.Sequence[ta.Tuple[str, str]]:
        fmt = f'%0{self.replacement_pad()}x'
        return [
            (l, self.escape + fmt % (i,))
            for i, l in enumerate(self.replaced())
        ]

    @cached_nullary
    def replacements_dict(self) -> ta.Mapping[str, str]:
        return dict(self.replacements())

    @cached_nullary
    def inverse_replacements_dict(self) -> ta.Mapping[str, str]:
        return {v: k for k, v in self.replacements()}

    @cached_nullary
    def replacements_pat(self) -> re.Pattern:
        return re.compile(''.join([re.escape(self.escape), '.' * self.replacement_pad()]))

    #

    # def mangle(self, s: str) -> str:
    #     ecs = sorted(
    #         frozenset(s) & self.replaced_set(),
    #         key=self.replaced_indexes().__getitem__,
    #         )
    #     rd = self.replacements_dict()
    #     for l in ecs:
    #         r = rd[l]
    #         s = s.replace(l, r)
    #     return s

    def mangle(self, s: str) -> str:
        rd = self.replacements_dict()
        return self.replaced_pat().sub(lambda m: rd[m.group(0)], s)

    #

    # def unmangle(self, s: str) -> str:
    #     for l, r in reversed(self.replacements()):
    #         s = s.replace(r, l)
    #     return s

    def unmangle(self, s: str) -> str:
        ird = self.inverse_replacements_dict()
        return self.replacements_pat().sub(lambda m: ird[m.group(0)], s)
