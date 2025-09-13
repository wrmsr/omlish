import typing as ta

from .base import Match
from .parsers import Concat
from .parsers import Either
from .parsers import Repeat
from .parsers import Rule


##


def strip_match_rules(m: Match, names: ta.Container[str]) -> Match:
    def rec(c: Match) -> Match:
        return c.flat_map_children(
            lambda x: (rec(x),) if not (isinstance((xp := x.parser), Rule) and xp.name in names) else (),  # noqa
        )
    return rec(m)


def collapse_match(m: Match) -> Match:
    def rec(c: Match) -> ta.Iterable[Match]:
        if isinstance(c.parser, Either) and len(c.children) == 1:
            return rec(c.children[0])
        elif isinstance(c.parser, Repeat) and c.length == 0:
            return ()
        elif isinstance(c.parser, Concat) and not c.children:
            return ()
        else:
            return (c.flat_map_children(rec),)
    return m.flat_map_children(rec)
