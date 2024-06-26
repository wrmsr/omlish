import typing as ta

from .. import dataclasses as dc
from .. import lang
from .binder import bind
from .elements import Element
from .elements import Elements


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Overrides(Element, lang.Final):
    ovr: Elements
    src: Elements


def override(ovr: ta.Any, *a: ta.Any) -> Element:
    return Overrides(bind(ovr), bind(*a))
