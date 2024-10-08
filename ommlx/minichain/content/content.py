"""
TODO:
 - metadata?
 - ListOfContent? what to name
"""
import typing as ta

from omlish import lang


##


Content: ta.TypeAlias = ta.Union[
    str,
    ta.Sequence['Content'],
    'ExtendedContent',
]


class ExtendedContent(lang.Abstract, lang.PackageSealed):
    pass
