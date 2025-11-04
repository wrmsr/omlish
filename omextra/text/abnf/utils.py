import itertools
import textwrap
import typing as ta

from omlish import check

from .base import Grammar
from .base import Match
from .errors import AbnfIncompleteParseError
from .parsers import RuleRef


##


def strip_insignificant_match_rules(m: Match, g: Grammar) -> Match:
    def rec(c: Match) -> Match:
        return c.flat_map_children(
            lambda x: (
                (rec(x),) if not (
                    isinstance((xp := x.parser), RuleRef) and
                    check.not_none(g.rule(xp.name)).insignificant
                ) else ()
            ),
        )
    return rec(m)


def only_match_rules(m: Match) -> Match:
    def rec(c: Match) -> ta.Iterable[Match]:
        if isinstance(c.parser, RuleRef):
            return (c.flat_map_children(rec),)
        else:
            return itertools.chain.from_iterable(map(rec, c.children))
    return m.flat_map_children(rec)


#


def parse_rules(
        grammar: Grammar,
        source: str,
        root: str | None = None,
        *,
        start: int = 0,
        complete: bool = False,
        **kwargs: ta.Any,
) -> Match | None:
    if (match := grammar.parse(
            source,
            root,
            start=start,
            **kwargs,
    )) is None:
        return None

    if complete and (match.start, match.end) != (start, len(source)):
        raise AbnfIncompleteParseError

    match = only_match_rules(match)
    match = strip_insignificant_match_rules(match, grammar)

    return match


##


def fix_grammar_ws(s: str) -> str:
    return (
        textwrap.dedent(s)
        .rstrip()
        .replace('\r', '')
        .replace('\n', '\r\n')
    ) + '\r\n'
