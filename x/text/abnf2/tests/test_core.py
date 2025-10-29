import itertools
import textwrap

import pytest

from omlish import check

from .. import base as ba
from .. import core as co
from .. import parsers as pa
from ..utils import only_match_rules
from ..utils import strip_insignificant_match_rules
from ..meta import META_GRAMMAR
from ..utils import fix_grammar_ws
from .meta import MetaGrammarRuleVisitor


CORE_GRAMMAR = ba.Grammar(*co.CORE_RULES)


@pytest.mark.parametrize('src', [chr(x) for x in itertools.chain(range(0x41, 0x5b), range(0x61, 0x7b))])
def test_alpha(src):
    m = check.not_none(CORE_GRAMMAR.parse(src, 'ALPHA'))
    assert src[m.start:m.end] == src


@pytest.mark.parametrize('src', [
    '',
    *[x*y for x, y in itertools.product([1, 2], [' ', '\t', '\r\n ', '\r\n\t'])],
])
def test_lwsp(src):
    m = CORE_GRAMMAR.parse(src, 'LWSP')
    print(m)
    # [m] = CORE_GRAMMAR.parse(src, 'LWSP')
    # assert src[m.start:m.end] == src


def test_meta() -> None:
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

    source = fix_grammar_ws(textwrap.dedent(source))

    ggm = check.not_none(META_GRAMMAR.parse(source, 'rulelist'))
    ggm = only_match_rules(ggm)
    ggm = strip_insignificant_match_rules(ggm, META_GRAMMAR)
    print(ggm.render(indent=2))

    check.isinstance(ggm.parser, pa.Repeat)
    mg_rv = MetaGrammarRuleVisitor(source)
    rules = [mg_rv.visit_match(gg_cm) for gg_cm in ggm.children]
    print(rules)
    rfc_gram = ba.Grammar(*rules, *co.CORE_RULES)

    rfc_m = rfc_gram.parse('Mon, 02 Jun 1982 00:00:00 GMT', 'HTTP-date')
    rfc_m = only_match_rules(rfc_m)
    rfc_m = strip_insignificant_match_rules(rfc_m, rfc_gram)
    print(rfc_m.render(indent=2))

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
