import textwrap
import typing as ta

from omlish import check

from .grammars import Grammar
from .grammars import Channel
from .matches import Match
from .matches import filter_matches
from .ops import RuleRef


##


def filter_match_channels(
        m: Match,
        g: Grammar,
        *,
        keep: ta.Container[Channel] | None = None,
        remove: ta.Container[Channel] | None = None,
        keep_children: bool = False,
) -> Match:
    if keep is None and remove is None:
        return m

    def fn(x: Match) -> bool:
        if not isinstance((rr := x.op), RuleRef):
            return False

        r = check.not_none(g.rule(rr.name))

        if keep is not None and r.channel not in keep:
            return False

        if remove is not None and r.channel in remove:
           return False

        return True

    return filter_matches(
        fn,
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

    match = filter_match_channels(match, grammar, remove=(Channel.SPACE,), keep_children=True)

    return match


##


def fix_ws(s: str) -> str:
    return (
        textwrap.dedent(s)
        .rstrip()
        .replace('\r', '')
        .replace('\n', '\r\n')
    ) + '\r\n'
