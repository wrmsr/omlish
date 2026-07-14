import typing as ta

from ...lite.json import JsonStyle


##


class Separators(ta.NamedTuple):
    comma: str
    colon: str


##


PRETTY_INDENT = 2

PRETTY_SEPARATORS = Separators(', ', ': ')

PRETTY_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=PRETTY_INDENT,
)


##


COMPACT_SEPARATORS = Separators(',', ':')

COMPACT_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=None,
    separators=COMPACT_SEPARATORS,
)


##


KWARGS_BY_STYLE: ta.Mapping[JsonStyle, ta.Mapping[str, ta.Any]] = {
    'pretty': PRETTY_KWARGS,
    'compact': COMPACT_KWARGS,
    None: {},
}
