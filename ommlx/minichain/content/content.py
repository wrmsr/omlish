"""
TODO:
 - metadata?
 - ListOfContent? what to name
"""
import typing as ta

from omlish import lang


##


class ExtendedContent(lang.Abstract, lang.PackageSealed):
    pass


##


SingleContent: ta.TypeAlias = ta.Union[  # noqa
    str,
    ExtendedContent,
]


Content: ta.TypeAlias = ta.Union[  # noqa
    ta.Sequence['Content'],
    SingleContent,
]
