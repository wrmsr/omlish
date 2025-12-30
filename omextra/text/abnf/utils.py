import textwrap
import typing as ta

from omlish import check

from .grammars import Grammar
from .grammars import Channel
from .matches import Match
from .matches import filter_matches
from .ops import RuleRef


##


def strip_insignificant_match_rules(
        m: Match,
        g: Grammar,
        *,
        keep_children: bool = False,
) -> Match:
    return filter_matches(
        lambda x: not (
                isinstance((xp := x.op), RuleRef) and
                check.not_none(g.rule(xp.name)).channel == Channel.SPACE
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


##


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
