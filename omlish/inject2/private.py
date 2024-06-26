import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .elements import Elements
from .keys import Key
from .keys import as_key


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Expose(Element, lang.Final):
    key: Key


def expose(k: ta.Any) -> Element:
    return Expose(as_key(k))


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Private(Element, lang.Final):
    elements: Elements


def private(es: Elements) -> Element:
    return Private(check.isinstance(es, Elements))
