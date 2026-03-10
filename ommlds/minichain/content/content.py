import typing as ta

from omlish import lang


##


class ContentBase(lang.Abstract, lang.PackageSealed):
    """
    Serves only as a root class for all non-typealias Content. All real Content should extend StandardContent, not this.
    """


##


Content: ta.TypeAlias = ta.Union[  # noqa
    str,
    ContentBase,
    ta.Sequence['Content'],
]


CONTENT_TYPES: tuple[type, ...] = (
    str,
    ContentBase,
    ta.Sequence,
)
