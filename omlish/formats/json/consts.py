import typing as ta


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
