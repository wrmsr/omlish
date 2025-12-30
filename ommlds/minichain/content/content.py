import typing as ta

from omlish import lang


##


class BaseContent(lang.Abstract, lang.PackageSealed):
    pass


##


Content: ta.TypeAlias = ta.Union[  # noqa
    str,
    BaseContent,
    ta.Sequence['Content'],
]


CONTENT_TYPES: tuple[type, ...] = (
    str,
    BaseContent,
    ta.Sequence,
)
