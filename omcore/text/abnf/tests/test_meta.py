import pytest

from .... import check
from ..errors import AbnfGrammarParseError
from ..grammars import Channel
from ..meta import parse_grammar
from ..ops import Either
from ..utils import filter_match_channels
from ..utils import only_match_rules


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

    rfc_gram = parse_grammar(source)

    rfc_m = rfc_gram.parse('Mon, 02 Jun 1982 00:00:00 GMT', 'HTTP-date')
    assert rfc_m is not None
    rfc_m = only_match_rules(rfc_m)
    rfc_m = filter_match_channels(rfc_m, rfc_gram, remove=(Channel.SPACE,))
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


##
# Extension: '|' first-match alternation


def test_pipe_alternation_first_match():
    g = parse_grammar(
        """
        slash = "x" / "xy"
        pipe  = "x" | "xy"
        """,
    )

    # '/' explores all branches - longest match wins
    m = g.parse('xy', 'slash')
    assert m is not None
    assert (m.start, m.end) == (0, 2)

    # '|' commits to the first matching branch
    m = g.parse('xy', 'pipe')
    assert m is not None
    assert (m.start, m.end) == (0, 1)


def test_pipe_alternation_op_flags():
    g = parse_grammar(
        """
        slash = "a" / "b"
        pipe  = "a" | "b"
        """,
        no_optimize=True,
    )

    slash_op = check.not_none(g.rule('slash')).op
    pipe_op = check.not_none(g.rule('pipe')).op

    assert isinstance(slash_op, Either)
    assert not slash_op.first_match

    assert isinstance(pipe_op, Either)
    assert pipe_op.first_match


def test_mixed_alternation_operators_rejected():
    with pytest.raises(AbnfGrammarParseError) as ei:
        parse_grammar(
            """
            bad = "a" / "b" | "c"
            """,
        )

    assert 'mix' in str(ei.value)


def test_mixed_alternation_operators_parenthesized_ok():
    g = parse_grammar(
        """
        ok = "a" / ("b" | "c")
        """,
    )

    assert g.parse('c', 'ok') is not None


def test_pipe_inside_quoted_string_is_literal():
    g = parse_grammar(
        """
        r = "|" / "x"
        """,
    )

    assert g.parse('|', 'r') is not None


##
# Extension: LF-tolerant meta-grammar


def test_lf_line_endings():
    g = parse_grammar('root = "a" 1*DIGIT\nother = "b"\n', root='root')

    assert g.parse('a42', complete=True) is not None


def test_crlf_line_endings():
    g = parse_grammar('root = "a" 1*DIGIT\r\nother = "b"\r\n', root='root')

    assert g.parse('a42', complete=True) is not None


def test_mixed_line_endings():
    g = parse_grammar('root = "a" 1*DIGIT\r\nother = "b"\n', root='root')

    assert g.parse('a42', complete=True) is not None


def test_no_trailing_newline():
    g = parse_grammar('root = "a"', root='root')

    assert g.parse('a', complete=True) is not None


def test_lf_comments_and_folding():
    g = parse_grammar(
        'root = "a"  ; a comment\n'
        '       / "b"\n'
        '; standalone comment\n'
        'other = "c"\n',
        root='root',
    )

    assert g.parse('b', complete=True) is not None


def test_grammar_error_line_position_unindented():
    # unindented LF sources go through parsing offset-exactly, so errors point at real lines
    with pytest.raises(AbnfGrammarParseError) as ei:
        parse_grammar(
            'root = "a"\n'
            'ok = "b"\n'
            'bad = &&&\n',
        )

    assert 'line 3' in str(ei.value)
