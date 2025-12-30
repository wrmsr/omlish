"""
https://datatracker.ietf.org/doc/html/rfc5234
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .base import Op
from .core import CORE_RULES
from .errors import AbnfGrammarParseError
from .grammars import Channel
from .grammars import Grammar
from .grammars import Rule
from .matches import Match
from .ops import Repeat
from .ops import concat
from .ops import either
from .ops import literal
from .ops import option
from .ops import repeat
from .ops import rule
from .opto import optimize_grammar
from .utils import filter_match_channels
from .utils import fix_ws
from .utils import only_match_rules
from .visitors import RuleMatchVisitor


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
        channel=Channel.SPACE,
    ),

    Rule(
        'c-nl',
        either(
            rule('comment'),
            rule('CRLF'),
        ),
        channel=Channel.SPACE,
    ),

    Rule(
        'comment',
        concat(
            literal(';'),
            repeat(
                either(
                    rule('WSP'),
                    rule('VCHAR'),
                ),
            ),
            rule('CRLF'),
        ),
        channel=Channel.COMMENT,
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


RAW_META_GRAMMAR = Grammar(
    *CORE_RULES,
    *META_GRAMMAR_RULES,
    root='rulelist',
)

META_GRAMMAR = optimize_grammar(
    RAW_META_GRAMMAR,
    inline_channels=(
        Channel.CONTENT,
        Channel.COMMENT,
        Channel.SPACE,
    ),
)


##


class MetaGrammarRuleMatchVisitor(RuleMatchVisitor[ta.Any]):
    def __init__(self, source: str) -> None:
        super().__init__()

        self._source = source

    @dc.dataclass(frozen=True)
    class RuleName(lang.Final):
        s: str

    @dc.dataclass(frozen=True)
    class QuotedString(lang.Final):
        s: str

    @RuleMatchVisitor.register('rule')
    def visit_rule_rule(self, m: Match) -> ta.Any:
        rn_m, _, el_m = m.children
        rn = check.isinstance(self.visit_match(rn_m), self.RuleName).s
        el = self.visit_match(el_m)
        return Rule(rn, el)

    @RuleMatchVisitor.register('rulename')
    def visit_rulename_rule(self, m: Match) -> ta.Any:
        return self.RuleName(self._source[m.start:m.end])

    @RuleMatchVisitor.register('elements')
    def visit_elements_rule(self, m: Match) -> ta.Any:
        return self.visit_match(check.single(m.children))

    @RuleMatchVisitor.register('alternation')
    def visit_alternation_rule(self, m: Match) -> ta.Any:
        if len(m.children) == 1:
            return self.visit_match(m.children[0])
        else:
            return either(*map(self.visit_match, m.children))

    @RuleMatchVisitor.register('concatenation')
    def visit_concatenation_rule(self, m: Match) -> ta.Any:
        if len(m.children) == 1:
            return self.visit_match(m.children[0])
        else:
            return concat(*map(self.visit_match, m.children))

    @RuleMatchVisitor.register('repetition')
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

    @RuleMatchVisitor.register('repeat')
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

    @RuleMatchVisitor.register('element')
    def visit_element_rule(self, m: Match) -> ta.Any:
        c = self.visit_match(check.single(m.children))
        if isinstance(c, Op):
            return c
        elif isinstance(c, self.RuleName):
            return rule(c.s)
        else:
            raise TypeError(c)

    @RuleMatchVisitor.register('group')
    def visit_group_rule(self, m: Match) -> ta.Any:
        return self.visit_match(check.single(m.children))

    @RuleMatchVisitor.register('option')
    def visit_option_rule(self, m: Match) -> ta.Any:
        c = self.visit_match(check.single(m.children))
        return option(check.isinstance(c, Op))

    @RuleMatchVisitor.register('num-val')
    def visit_num_val_rule(self, m: Match) -> ta.Any:
        return self.visit_match(check.single(m.children))

    def _parse_num_val(self, s: str, base: int) -> Op:
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

    @RuleMatchVisitor.register('dec-val')
    def visit_dec_val_rule(self, m: Match) -> ta.Any:
        return self._parse_num_val(self._source[m.start + 1:m.end], 10)

    @RuleMatchVisitor.register('hex-val')
    def visit_hex_val_rule(self, m: Match) -> ta.Any:
        return self._parse_num_val(self._source[m.start + 1:m.end], 16)

    @RuleMatchVisitor.register('char-val')
    def visit_char_val_rule(self, m: Match) -> ta.Any:
        return self.visit_match(check.single(m.children))

    @RuleMatchVisitor.register('case-sensitive-string')
    def visit_case_sensitive_string_rule(self, m: Match) -> ta.Any:
        c = self.visit_match(check.single(m.children))
        return literal(check.isinstance(c, self.QuotedString).s, case_sensitive=True)

    @RuleMatchVisitor.register('case-insensitive-string')
    def visit_case_insensitive_string_rule(self, m: Match) -> ta.Any:
        c = self.visit_match(check.single(m.children))
        return literal(check.isinstance(c, self.QuotedString).s, case_sensitive=False)

    @RuleMatchVisitor.register('quoted-string')
    def visit_quoted_string_rule(self, m: Match) -> ta.Any:
        check.state(m.end - m.start > 2)
        check.state(self._source[m.start] == '"')
        check.state(self._source[m.end - 1] == '"')
        return self.QuotedString(self._source[m.start + 1:m.end - 1])


##


def parse_grammar(
        source: str,
        *,
        root: str | None = None,
        no_core_rules: bool = False,
        no_optimize: bool = False,
        **kwargs: ta.Any,
) -> Grammar:
    source = fix_ws(source)

    if (mg_m := META_GRAMMAR.parse(
            source,
            complete=True,
            **kwargs,
    )) is None:
        raise AbnfGrammarParseError(source)

    mg_m = only_match_rules(mg_m)

    mg_m = filter_match_channels(
        mg_m,
        META_GRAMMAR,
        keep=(Channel.STRUCTURE,),
        keep_children=True,
    )

    check.isinstance(mg_m.op, Repeat)

    mg_rmv = MetaGrammarRuleMatchVisitor(source)
    rules = [
        check.isinstance(mg_rmv.visit_match(gg_cm), Rule)
        for gg_cm in mg_m.children
    ]

    gram = Grammar(
        *rules,
        *(CORE_RULES if not no_core_rules else []),
        root=root,
    )

    if not no_optimize:
        gram = optimize_grammar(gram)

    return gram
