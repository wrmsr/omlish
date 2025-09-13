import typing as ta
import itertools

from .base import Match
from .parsers import RuleRef


##


def strip_match_rules(m: Match, names: ta.Container[str]) -> Match:
    def rec(c: Match) -> Match:
        return c.flat_map_children(
            lambda x: (rec(x),) if not (isinstance((xp := x.parser), RuleRef) and xp.name in names) else (),  # noqa
        )
    return rec(m)


def only_match_rules(m: Match, *, exclude: ta.Container[str] | None = None) -> Match:
    def rec(c: Match) -> ta.Iterable[Match]:
        if isinstance(c.parser, RuleRef):
            if exclude is not None and c.parser.name in exclude:
                return ()
            else:
                return (c.flat_map_children(rec),)
        else:
            return itertools.chain.from_iterable(map(rec, c.children))
    return m.flat_map_children(rec)
