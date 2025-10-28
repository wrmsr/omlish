import functools
import itertools
import textwrap
import typing as ta

import pytest

from omlish import check
from omlish import dataclasses as dc

from .. import base as ba
from .. import core as co
from .. import parsers as pa
from .. import utils as ut


CORE_GRAMMAR = ba.Grammar(*co.CORE_RULES)


@pytest.mark.parametrize('src', [chr(x) for x in itertools.chain(range(0x41, 0x5b), range(0x61, 0x7b))])
def test_alpha(src):
    m = check.not_none(CORE_GRAMMAR.parse(src, 'ALPHA'))
    assert src[m.start:m.end] == src


@dc.dataclass(frozen=True)
class RuleName:
    s: str


@dc.dataclass(frozen=True)
class QuotedString:
    s: str


@pytest.mark.parametrize('src', [
    '',
    *[x*y for x, y in itertools.product([1, 2], [' ', '\t', '\r\n ', '\r\n\t'])],
])
def test_lwsp(src):
    m = CORE_GRAMMAR.parse(src, 'LWSP')
    print(m)
    # [m] = CORE_GRAMMAR.parse(src, 'LWSP')
    # assert src[m.start:m.end] == src


def test_core() -> None:
    @functools.singledispatch
    def visit_parser(p: ba.Parser, m: ba.Match) -> ta.Any:
        raise TypeError(p)

    @visit_parser.register
    def visit_rule_ref_parser(p: pa.RuleRef, m: ba.Match) -> ta.Any:
        # print(p.name)
        # for c in m.children:
        #     visit_match(c)
        return rule_fns[p.name](m)

    @visit_parser.register
    def visit_repeat_parser(p: pa.Repeat, m: ba.Match) -> ta.Any:
        return [visit_match(cm) for cm in m.children]

    #

    rule_fns = {}

    def add_rule_fn(*names):
        def inner(fn):
            rule_fns.update({n: fn for n in names})
            return fn
        return inner

    @add_rule_fn('rule')
    def visit_rule_rule(m: ba.Match) -> ta.Any:
        rn_m, _, el_m = m.children
        rn = check.isinstance(visit_match(rn_m), RuleName).s
        el = visit_match(el_m)
        return ba.Rule(rn, el)

    @add_rule_fn('rulename')
    def visit_rulename_rule(m: ba.Match) -> ta.Any:
        return RuleName(source[m.start:m.end])

    @add_rule_fn('elements')
    def visit_elements_rule(m: ba.Match) -> ta.Any:
        return visit_match(check.single(m.children))

    @add_rule_fn('alternation')
    def visit_alternation_rule(m: ba.Match) -> ta.Any:
        if len(m.children) == 1:
            return visit_match(m.children[0])
        else:
            return pa.either(*map(visit_match, m.children))

    @add_rule_fn('concatenation')
    def visit_concatenation_rule(m: ba.Match) -> ta.Any:
        if len(m.children) == 1:
            return visit_match(m.children[0])
        else:
            return pa.concat(*map(visit_match, m.children))

    @add_rule_fn('repetition')
    def visit_repetition_rule(m: ba.Match) -> ta.Any:
        if len(m.children) == 2:
            ti_m, el_m = m.children
            ti = check.isinstance(visit_match(ti_m), pa.Repeat.Times)
            el = visit_match(el_m)
            return pa.repeat(ti, el)
        elif len(m.children) == 1:
            return visit_match(m.children[0])
        else:
            raise ValueError(m)

    @add_rule_fn('element')
    def visit_element_rule(m: ba.Match) -> ta.Any:
        c = visit_match(check.single(m.children))
        if isinstance(c, ba.Parser):
            return c
        elif isinstance(c, RuleName):
            return pa.rule(c.s)
        else:
            raise TypeError(c)

    @add_rule_fn('char-val')
    def visit_char_val_rule(m: ba.Match) -> ta.Any:
        return visit_match(check.single(m.children))

    @add_rule_fn('case-sensitive-string')
    def visit_case_sensitive_string_rule(m: ba.Match) -> ta.Any:
        c = visit_match(check.single(m.children))
        return pa.literal(check.isinstance(c, QuotedString).s, case_sensitive=True)

    @add_rule_fn('case-insensitive-string')
    def visit_case_insensitive_string_rule(m: ba.Match) -> ta.Any:
        c = visit_match(check.single(m.children))
        return pa.literal(check.isinstance(c, QuotedString).s, case_sensitive=False)

    @add_rule_fn('quoted-string')
    def visit_quoted_string_rule(m: ba.Match) -> ta.Any:
        check.state(m.end - m.start > 2)
        check.state(source[m.start] == '"')
        check.state(source[m.end - 1] == '"')
        return QuotedString(source[m.start + 1:m.end - 1])

    @add_rule_fn('repeat')
    def visit_repeat_rule(m: ba.Match) -> ta.Any:
        s = source[m.start:m.end]
        if '*' in s:
            raise NotImplementedError
        return pa.Repeat.Times(int(s))

    #

    def visit_match(m: ba.Match) -> ta.Any:
        return visit_parser(m.parser, m)

    ##

    # # rfc_2616
    source = r"""
        HTTP-date    = rfc1123-date / rfc850-date / asctime-date
        rfc1123-date = wkday "," SP date1 SP time SP "GMT"
        rfc850-date  = weekday "," SP date2 SP time SP "GMT"
        asctime-date = wkday SP date3 SP time SP 4DIGIT
        date1        = 2DIGIT SP month SP 4DIGIT          ; day month year (e.g., 02 Jun 1982)
        date2        = 2DIGIT "-" month "-" 2DIGIT        ; day-month-year (e.g., 02-Jun-82)
        date3        = month SP ( 2DIGIT / ( SP 1DIGIT )) ; month day (e.g., Jun  2)
        time         = 2DIGIT ":" 2DIGIT ":" 2DIGIT       ; 00:00:00 - 23:59:59
        wkday        = "Mon" / "Tue" / "Wed" / "Thu" / "Fri" / "Sat" / "Sun"
        weekday      = "Monday" / "Tuesday" / "Wednesday" / "Thursday" / "Friday" / "Saturday" / "Sunday"
        month        = "Jan" / "Feb" / "Mar" / "Apr" / "May" / "Jun" / "Jul" / "Aug" / "Sep" / "Oct" / "Nov" / "Dec"

        token        = 1*( %x21 / %x23-27 / %x2A-2B / %x2D-2E / %x30-39 / %x41-5A / %x5E-7A / %x7C )
    """

    source = co.fix_grammar_ws(textwrap.dedent(source))
    ggm = check.not_none(co.GRAMMAR_GRAMMAR.parse(source, 'rulelist'))
    ggm = ut.only_match_rules(ggm)
    ggm = ut.strip_insignificant_match_rules(ggm, co.GRAMMAR_GRAMMAR)
    print(ggm.render(indent=2))
    # for rm in ggm.children:
    print(visit_match(ggm))

    # g = Grammar(
    #     CORE_RULES,
    #     {'root': concat(
    #         repeat(rule('WSP')),
    #         repeat(1, literal('a', 'z')),
    #         repeat(rule('WSP')),
    #         literal('='),
    #         repeat(rule('WSP')),
    #         literal('"'),
    #         repeat(
    #             either(
    #                 literal('a', 'z'),
    #                 literal(' '),
    #             ),
    #         ),
    #         literal('"'),
    #     )},
    #     root='root',
    # )
    # for s in [
    #     'x = "y"',
    #     'x=  "y"',
    #     'xy= "az"',
    # ]:
    #     m = g.parse(s)
    #     print(m)
