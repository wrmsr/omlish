from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .elements import Elemental
from .elements import Elements
from .elements import as_elements
from .keys import Key
from .keys import as_key


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Expose(Element, lang.Final):
    key: Key = dc.xfield(coerce=as_key)


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Private(Element, lang.Final):
    elements: Elements = dc.xfield(coerce=check.of_isinstance(Elements))


def private(*args: Elemental) -> Private:
    return Private(as_elements(*args))
