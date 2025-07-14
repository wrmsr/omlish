import typing as ta

from omlish import lang


##


class ExtendedContent(lang.Abstract, lang.PackageSealed):
    pass


class SingleExtendedContent(ExtendedContent, lang.Abstract):
    pass


##


Content: ta.TypeAlias = ta.Union[  # noqa
    str,
    ExtendedContent,
    ta.Sequence['Content'],
]


SingleContent: ta.TypeAlias = ta.Union[  # noqa
    str,
    SingleExtendedContent,
]
