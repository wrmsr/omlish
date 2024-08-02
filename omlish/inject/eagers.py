"""
TODO:
 - SCOPED - eagers for EACH SCOPE
"""
from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .keys import Key


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Eager(Element, lang.Final):
    key: Key = dc.xfield(coerce=check.of_isinstance(Key))
