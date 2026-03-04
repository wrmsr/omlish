import typing as ta

from omlish import lang


##


class BaseContent(lang.Abstract, lang.PackageSealed):
    """
    Serves only as a root class for all non-typealias Content. All real Content should extend StandardContent, not this.
    """


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
