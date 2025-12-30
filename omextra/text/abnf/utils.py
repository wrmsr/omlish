import textwrap
import typing as ta

from omlish import check
from omlish import lang

from .grammars import Grammar
from .matches import Match
from .ops import RuleRef


##


def filter_matches(
        fn: ta.Callable[[Match], bool],
        m: Match,
        *,
        keep_children: bool = False,
) -> Match:
    def inner(x: Match) -> ta.Iterable[Match]:
        if fn(x):
            return (rec(x),)

        elif keep_children:
            return lang.flatten(inner(c) for c in x.children)

        else:
            return ()

    def rec(c: Match) -> Match:
        return c.flat_map_children(inner)

    return rec(m)


#


def strip_insignificant_match_rules(
        m: Match,
        g: Grammar,
        *,
        keep_children: bool = False,
) -> Match:
    return filter_matches(
        lambda x: not (
                isinstance((xp := x.op), RuleRef) and
                check.not_none(g.rule(xp.name)).insignificant
        ),
        m,
        keep_children=keep_children,
    )


#


def only_match_rules(m: Match) -> Match:
    return filter_matches(
        lambda x: isinstance(x.op, RuleRef),
        m,
        keep_children=True,
    )


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
    match = strip_insignificant_match_rules(match, grammar, keep_children=True)

    return match


##


def fix_ws(s: str) -> str:
    return (
        textwrap.dedent(s)
        .rstrip()
        .replace('\r', '')
        .replace('\n', '\r\n')
    ) + '\r\n'
