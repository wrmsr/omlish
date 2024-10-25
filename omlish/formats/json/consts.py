import typing as ta


##


PRETTY_INDENT = 2

PRETTY_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=PRETTY_INDENT,
)


##


COMPACT_SEPARATORS = (',', ':')

COMPACT_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=None,
    separators=COMPACT_SEPARATORS,
)
