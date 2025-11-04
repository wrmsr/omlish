"""
https://datatracker.ietf.org/doc/html/rfc5234
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .base import Grammar
from .base import Match
from .base import Parser
from .base import Rule
from .core import CORE_RULES
from .errors import AbnfGrammarParseError
from .parsers import Repeat
from .parsers import concat
from .parsers import either
from .parsers import literal
from .parsers import option
from .parsers import repeat
from .parsers import rule
from .utils import fix_grammar_ws
from .utils import parse_rules
from .visitors import RuleVisitor


##


META_GRAMMAR_RULES: ta.Sequence[Rule] = [

    Rule(
        'rulelist',
        repeat(
            1,
            either(
                rule('rule'),
                concat(
                    repeat(
                        rule('c-wsp'),
                    ),
                    rule('c-nl'),
                ),
            ),
        ),
    ),

    Rule(
        'rule',
        concat(
            rule('rulename'),
            rule('defined-as'),
            rule('elements'),
            rule('c-nl'),
        ),
    ),

    Rule(
        'rulename',
        concat(
            rule('ALPHA'),
            repeat(
                either(
                    rule('ALPHA'),
                    rule('DIGIT'),
                    literal('-'),
                ),
            ),
        ),
    ),

    Rule(
        'defined-as',
        concat(
            repeat(
                rule('c-wsp'),
            ),
            either(
                literal('=/'),
                literal('='),
            ),
            repeat(
                rule('c-wsp'),
            ),
        ),
    ),

    Rule(
        'elements',
        concat(
            rule('alternation'),
            repeat(
                rule('c-wsp'),
            ),
        ),
    ),

    Rule(
        'c-wsp',
        either(
            rule('WSP'),
            concat(
                rule('c-nl'),
                rule('WSP'),
            ),
        ),
        insignificant=True,
    ),

    Rule(
        'c-nl',
        either(
            rule('comment'),
            rule('CRLF'),
        ),
        insignificant=True,
    ),

    Rule(
        'comment',
        concat(
            literal(';'),
            repeat(
                either(
                    rule('WSP'),
                    rule('VCHAR'),
                )),
            rule('CRLF'),
        ),
    ),

    Rule(
        'alternation',
        concat(
            rule('concatenation'),
            repeat(
                concat(
                    repeat(
                        rule('c-wsp'),
                    ),
                    literal('/'),
                    repeat(
                        rule('c-wsp'),
                    ),
                    rule('concatenation'),
                ),
            ),
        ),
    ),

    Rule(
        'concatenation',
        concat(
            rule('repetition'),
            repeat(
                concat(
                    repeat(
                        1,
                        rule('c-wsp'),
                    ),
                    rule('repetition'),
                ),
            ),
        ),
    ),

    Rule(
        'repetition',
        concat(
            option(
                rule('repeat'),
            ),
            rule('element'),
        ),
    ),

    Rule(
        'repeat',
        either(
            concat(
                repeat(
                    rule('DIGIT'),
                ),
                literal('*'),
                repeat(
                    rule('DIGIT'),
                ),
            ),
            repeat(
                1,
                rule('DIGIT'),
            ),
        ),
    ),

    Rule(
        'element',
        either(
            rule('rulename'),
            rule('group'),
            rule('option'),
            rule('char-val'),
            rule('num-val'),
            rule('prose-val'),
        ),
    ),

    Rule(
        'group',
        concat(
            literal('('),
            repeat(
                rule('c-wsp'),
            ),
            rule('alternation'),
            repeat(
                rule('c-wsp'),
            ),
            literal(')'),
        ),
    ),

    Rule(
        'option',
        concat(
            literal('['),
            repeat(
                rule('c-wsp'),
            ),
            rule('alternation'),
            repeat(
                rule('c-wsp'),
            ),
            literal(']'),
        ),
    ),

    Rule(
        'num-val',
        concat(
            literal('%'),
            either(
                rule('bin-val'),
                rule('dec-val'),
                rule('hex-val'),
            ),
        ),
    ),

    Rule(
        'bin-val',
        concat(
            literal('b'),
            concat(
                repeat(
                    1,
                    rule('BIT'),
                ),
                option(
                    either(
                        repeat(
                            1,
                            concat(
                                literal('.'),
                                repeat(
                                    1,
                                    rule('BIT'),
                                ),
                            ),
                        ),
                        concat(
                            literal('-'),
                            repeat(
                                1,
                                rule('BIT'),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),

    Rule(
        'dec-val',
        concat(
            literal('d'),
            concat(
                repeat(
                    1,
                    rule('DIGIT'),
                ),
                option(
                    either(
                        repeat(
                            1,
                            concat(
                                literal('.'),
                                repeat(
                                    1,
                                    rule('DIGIT'),
                                ),
                            ),
                        ),
                        concat(
                            literal('-'),
                            repeat(
                                1,
                                rule('DIGIT'),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),

    Rule(
        'hex-val',
        concat(
            literal('x'),
            concat(
                repeat(
                    1,
                    rule('HEXDIG'),
                ),
                option(
                    either(
                        repeat(
                            1,
                            concat(
                                literal('.'),
                                repeat(
                                    1,
                                    rule('HEXDIG'),
                                ),
                            ),
                        ),
                        concat(
                            literal('-'),
                            repeat(
                                1,
                                rule('HEXDIG'),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),

    Rule(
        'prose-val',
        concat(
            literal('<'),
            repeat(
                either(
                    literal('\x20', '\x3d'),
                    literal('\x3f', '\x7e'),
                ),
            ),
            literal('>'),
        ),
    ),

    # definitions from RFC 7405
    Rule(
        'char-val',
        either(
            rule('case-insensitive-string'),
            rule('case-sensitive-string'),
        ),
    ),

    Rule(
        'case-insensitive-string',
        concat(
            option(
                literal('%i'),
            ),
            rule('quoted-string'),
        ),
    ),

    Rule(
        'case-sensitive-string',
        concat(
            literal('%s'),
            rule('quoted-string'),
        ),
    ),

    Rule(
        'quoted-string',
        concat(
            rule('DQUOTE'),
            repeat(
                either(
                    literal('\x20', '\x21'),
                    literal('\x23', '\x7e'),
                ),
            ),
            rule('DQUOTE'),
        ),
    ),

]


META_GRAMMAR = Grammar(
    *CORE_RULES,
    *META_GRAMMAR_RULES,
    root='rulelist',
)


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

    @RuleVisitor.register('repeat')
    def visit_repeat_rule(self, m: Match) -> ta.Any:
        s = check.non_empty_str(self._source[m.start:m.end])
        if s == '*':
            return Repeat.Times(0)
        elif '*' in s:
            check.state(s.count('*') == 1)
            if s.endswith('*'):
                return Repeat.Times(int(s[:-1]))
            else:
                mi, mx = s.split('*')
                return Repeat.Times(int(mi), int(mx))
        else:
            return Repeat.Times(n := int(s), n)

    @RuleVisitor.register('element')
    def visit_element_rule(self, m: Match) -> ta.Any:
        c = self.visit_match(check.single(m.children))
        if isinstance(c, Parser):
            return c
        elif isinstance(c, self.RuleName):
            return rule(c.s)
        else:
            raise TypeError(c)

    @RuleVisitor.register('group')
    def visit_group_rule(self, m: Match) -> ta.Any:
        return self.visit_match(check.single(m.children))

    @RuleVisitor.register('option')
    def visit_option_rule(self, m: Match) -> ta.Any:
        c = self.visit_match(check.single(m.children))
        return option(check.isinstance(c, Parser))

    @RuleVisitor.register('num-val')
    def visit_num_val_rule(self, m: Match) -> ta.Any:
        return self.visit_match(check.single(m.children))

    def _parse_num_val(self, s: str, base: int) -> Parser:
        if '-' in s:
            check.not_in('.', s)
            lo, hi = [chr(int(p, base)) for p in s.split('-')]
            return literal(lo, hi)
        elif '.' in s:
            check.not_in('-', s)
            cs = [chr(int(p, base)) for p in s.split('.')]
            return concat(*[literal(c, c) for c in cs])
        else:
            c = chr(int(s, base))
            return literal(c, c)

    @RuleVisitor.register('dec-val')
    def visit_dec_val_rule(self, m: Match) -> ta.Any:
        return self._parse_num_val(self._source[m.start + 1:m.end], 10)

    @RuleVisitor.register('hex-val')
    def visit_hex_val_rule(self, m: Match) -> ta.Any:
        return self._parse_num_val(self._source[m.start + 1:m.end], 16)

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


def parse_grammar(
        source: str,
        *,
        no_core_rules: bool = False,
        root: str | None = None,
        **kwargs: ta.Any,
) -> Grammar:
    source = fix_grammar_ws(source)

    if (mg_m := parse_rules(
            META_GRAMMAR,
            source,
            complete=True,
            **kwargs,
    )) is None:
        raise AbnfGrammarParseError(source)

    check.isinstance(mg_m.parser, Repeat)

    mg_rv = MetaGrammarRuleVisitor(source)
    rules = [mg_rv.visit_match(gg_cm) for gg_cm in mg_m.children]

    return Grammar(
        *rules,
        *(CORE_RULES if not no_core_rules else []),
        root=root,
    )
