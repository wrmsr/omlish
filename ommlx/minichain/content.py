"""
TODO:
 - metadata?
 - ListOfContent? what to name
"""
import dataclasses as dc

from omlish import lang


##


class Content(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class Text(Content, lang.Final):
    s: str
