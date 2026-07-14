from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class EmphasisContent(StandardContent, lang.Abstract):
    s: str


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class BoldContent(EmphasisContent, lang.Final):
    pass


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class ItalicContent(EmphasisContent, lang.Final):
    pass


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class BoldItalicContent(EmphasisContent, lang.Final):
    pass
