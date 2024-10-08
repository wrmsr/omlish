"""
TODO:
 - metadata?
 - ListOfContent? what to name
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


Contentable: ta.TypeAlias = ta.Union['Content', str]


class Content(lang.Abstract, lang.PackageSealed):
    @classmethod
    def of(cls, v: Contentable) -> 'Content':
        if isinstance(v, Content):
            return v
        elif isinstance(v, str):
            return Text(v)
        else:
            raise TypeError(v)


@dc.dataclass(frozen=True)
class Text(Content, lang.Final):
    s: str
