import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .elements import Elements
from .elements import as_elements


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Overrides(Element, lang.Final):
    ovr: Elements = dc.xfield(coerce=check.of_isinstance(Elements))
    src: Elements = dc.xfield(coerce=check.of_isinstance(Elements))


def override(ovr: ta.Any, *a: ta.Any) -> Element:
    return Overrides(as_elements(ovr), as_elements(*a))
