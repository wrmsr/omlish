from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .keys import Key
from .providers import Provider
from .types import Scope
from .types import Unscoped


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class Binding(Element, lang.Final):
    key: Key = dc.xfield(coerce=check.of_isinstance(Key))
    provider: Provider = dc.xfield(coerce=check.of_isinstance(Provider))
    scope: Scope = dc.xfield(default=Unscoped(), coerce=check.of_isinstance(Scope))
