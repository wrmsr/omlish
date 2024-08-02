from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .elements import Elements
from .keys import Key


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Expose(Element, lang.Final):
    key: Key = dc.xfield(coerce=check.of_isinstance(Key))


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Private(Element, lang.Final):
    elements: Elements = dc.xfield(coerce=check.of_isinstance(Elements))
