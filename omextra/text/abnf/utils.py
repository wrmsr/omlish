import itertools
import textwrap
import typing as ta

from omlish import check
from omlish import lang

from .grammars import Grammar
from .matches import Match
from .ops import RuleRef


##


def strip_insignificant_match_rules(
        m: Match,
        g: Grammar,
        *,
        remove_children: bool = False,
) -> Match:
    def fn(x: Match) -> ta.Iterable[Match]:
        if not (
                isinstance((xp := x.op), RuleRef) and
                check.not_none(g.rule(xp.name)).insignificant
        ):
            return (rec(x),)

        elif remove_children:
            return ()

        else:
            return lang.flatten(rec(c) for c in x.children)

    def rec(c: Match) -> Match:
        return c.flat_map_children(fn)

    return rec(m)


def only_match_rules(m: Match) -> Match:
    def rec(c: Match) -> ta.Iterable[Match]:
        if isinstance(c.op, RuleRef):
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
        **kwargs: ta.Any,
) -> Match | None:
    if (match := grammar.parse(
            source,
            root,
            start=start,
            **kwargs,
    )) is None:
        return None

    match = only_match_rules(match)
    match = strip_insignificant_match_rules(match, grammar)

    print(match.render(indent=2))

    return match


##


def fix_ws(s: str) -> str:
    return (
        textwrap.dedent(s)
        .rstrip()
        .replace('\r', '')
        .replace('\n', '\r\n')
    ) + '\r\n'
