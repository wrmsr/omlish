from omcore import dataclasses as dc
from omcore import lang

from .standard import StandardContent


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class LinkContent(StandardContent, lang.Final):
    url: str

    _: dc.KW_ONLY

    title: str | None = None
