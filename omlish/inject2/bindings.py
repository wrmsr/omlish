import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .keys import as_key
from .providers import ConstProvider
from .providers import Provider
from .providers import as_provider
from .providers import ctor as ctor_provider
from .providers import fn as fn_provider
from .elements import Element
from .elements import Elements
from .keys import Key


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Binding(Element, lang.Final):
    key: Key
    provider: Provider
    # scope: ScopeTag


##


def as_binding(o: ta.Any) -> Binding:
    check.not_none(o)
    check.not_isinstance(o, (Element, Elements))
    if isinstance(o, Binding):
        return o
    if isinstance(o, Provider):
        return Binding(Key(check.not_none(o.provided_cls())), o)  # noqa
    if isinstance(o, type):
        return as_binding(ctor_provider(o))
    if callable(o):
        return as_binding(fn_provider(o))
    cls = type(o)
    return Binding(Key(cls), ConstProvider(cls, o))


def as_(k: ta.Any, p: ta.Any) -> Binding:
    return Binding(as_key(k), as_provider(p))
