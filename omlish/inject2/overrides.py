import typing as ta

from .. import dataclasses as dc
from .binder import bind
from .elements import Element
from .elements import Elements


@dc.dataclass(frozen=True, eq=False)
class Overrides(Element):
    ovr: Elements
    src: Elements


def override(ovr: ta.Any, *a: ta.Any) -> Element:
    return Overrides(bind(ovr), bind(*a))
