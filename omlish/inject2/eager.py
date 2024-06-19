import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .bindings import Binding
from .bindings import as_binding
from .elements import Element
from .elements import Elements
from .keys import Key


@dc.dataclass(frozen=True)
class Eager(Element, lang.Final):
    key: Key


def eager(*args: ta.Any) -> Elements:
    bs = [check.isinstance(as_binding(a), Binding) for a in args]
    return Elements([*bs, *(Eager(b.key) for b in bs)])
