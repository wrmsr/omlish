"""
TODO:
 - SCOPED - eagers for EACH SCOPE
"""
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .keys import Key
from .keys import as_key


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Eager(Element, lang.Final):
    key: Key


def eager(k: ta.Any) -> Element:
    return Eager(as_key(k))
