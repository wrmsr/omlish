import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ..base import Match
from ..base import Parser
from ..base import Rule
from ..parsers import Repeat
from ..parsers import concat
from ..parsers import either
from ..parsers import literal
from ..parsers import repeat
from ..parsers import rule
from .visitors import RuleVisitor


##


class MetaGrammarRuleVisitor(RuleVisitor[ta.Any]):
    def __init__(self, source: str) -> None:
        super().__init__()

        self._source = source

    @dc.dataclass(frozen=True)
    class RuleName(lang.Final):
        s: str

    @dc.dataclass(frozen=True)
    class QuotedString(lang.Final):
        s: str

    @RuleVisitor.register('rule')
    def visit_rule_rule(self, m: Match) -> ta.Any:
        rn_m, _, el_m = m.children
        rn = check.isinstance(self.visit_match(rn_m), self.RuleName).s
        el = self.visit_match(el_m)
        return Rule(rn, el)

    @RuleVisitor.register('rulename')
    def visit_rulename_rule(self, m: Match) -> ta.Any:
        return self.RuleName(self._source[m.start:m.end])

    @RuleVisitor.register('elements')
    def visit_elements_rule(self, m: Match) -> ta.Any:
        return self.visit_match(check.single(m.children))

    @RuleVisitor.register('alternation')
    def visit_alternation_rule(self, m: Match) -> ta.Any:
        if len(m.children) == 1:
            return self.visit_match(m.children[0])
        else:
            return either(*map(self.visit_match, m.children))

    @RuleVisitor.register('concatenation')
    def visit_concatenation_rule(self, m: Match) -> ta.Any:
        if len(m.children) == 1:
            return self.visit_match(m.children[0])
        else:
            return concat(*map(self.visit_match, m.children))

    @RuleVisitor.register('repetition')
    def visit_repetition_rule(self, m: Match) -> ta.Any:
        if len(m.children) == 2:
            ti_m, el_m = m.children
            ti = check.isinstance(self.visit_match(ti_m), Repeat.Times)
            el = self.visit_match(el_m)
            return repeat(ti, el)
        elif len(m.children) == 1:
            return self.visit_match(m.children[0])
        else:
            raise ValueError(m)

    @RuleVisitor.register('element')
    def visit_element_rule(self, m: Match) -> ta.Any:
        c = self.visit_match(check.single(m.children))
        if isinstance(c, Parser):
            return c
        elif isinstance(c, self.RuleName):
            return rule(c.s)
        else:
            raise TypeError(c)

    @RuleVisitor.register('char-val')
    def visit_char_val_rule(self, m: Match) -> ta.Any:
        return self.visit_match(check.single(m.children))

    @RuleVisitor.register('case-sensitive-string')
    def visit_case_sensitive_string_rule(self, m: Match) -> ta.Any:
        c = self.visit_match(check.single(m.children))
        return literal(check.isinstance(c, self.QuotedString).s, case_sensitive=True)

    @RuleVisitor.register('case-insensitive-string')
    def visit_case_insensitive_string_rule(self, m: Match) -> ta.Any:
        c = self.visit_match(check.single(m.children))
        return literal(check.isinstance(c, self.QuotedString).s, case_sensitive=False)

    @RuleVisitor.register('quoted-string')
    def visit_quoted_string_rule(self, m: Match) -> ta.Any:
        check.state(m.end - m.start > 2)
        check.state(self._source[m.start] == '"')
        check.state(self._source[m.end - 1] == '"')
        return self.QuotedString(self._source[m.start + 1:m.end - 1])

    @RuleVisitor.register('repeat')
    def visit_repeat_rule(self, m: Match) -> ta.Any:
        # !!! FIXME: boneheaded args, repeat(1, c) currently means 1-*, should be exactly 1-1, should explicitly pass
        #            None for *
        s = self._source[m.start:m.end]
        if '*' in s:
            check.state(s.count('*') == 1)
            if s.endswith('*'):
                return Repeat.Times(int(s[:-1]))
            else:
                mi, mx = s.split('*')
                return Repeat.Times(int(mi), int(mx))
        else:
            return Repeat.Times(n := int(s), n)

    @RuleVisitor.register('group')
    def visit_group_rule(self, m: Match) -> ta.Any:
        return self.visit_match(check.single(m.children))

    @RuleVisitor.register('num-val')
    def visit_num_val_rule(self, m: Match) -> ta.Any:
        return self.visit_match(check.single(m.children))

    @RuleVisitor.register('hex-val')
    def visit_hex_val_rule(self, m: Match) -> ta.Any:
        s = self._source[m.start + 1:m.end]
        if '-' in s:
            lo, hi = [chr(int(p, 16)) for p in s.split('-')]
            return literal(lo, hi)
        else:
            c = chr(int(s, 16))
            return literal(c, c)
