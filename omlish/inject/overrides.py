import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .elements import Elemental
from .elements import Elements
from .elements import as_elements


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class Overrides(Element, lang.Final):
    src: Elements = dc.xfield(coerce=check.of_isinstance(Elements))
    ovr: Elements = dc.xfield(coerce=check.of_isinstance(Elements))


def override(src: ta.Any, *ovr: ta.Any) -> Elemental:
    sce = as_elements(src)
    ove = as_elements(*ovr)
    if not lang.ilen(ove):
        return sce
    return Overrides(sce, ove)
