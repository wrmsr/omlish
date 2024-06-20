import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .elements import Elements
from .keys import Key
from .keys import as_key
from .providers import Provider
from .providers import as_provider
from .providers import const
from .providers import ctor
from .providers import fn
from .scopes import Scope
from .scopes import Singleton
from .scopes import Unscoped


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class Binding(Element, lang.Final):
    key: Key
    provider: Provider
    scope: Scope = Unscoped()


##


def as_binding(o: ta.Any) -> Binding:
    check.not_none(o)
    if isinstance(o, Binding):
        return o
    check.not_isinstance(o, (Element, Elements))
    if isinstance(o, Provider):
        return Binding(Key(check.not_none(o.provided_cls())), o)  # type: ignore  # noqa
    if isinstance(o, type):
        return as_binding(ctor(o))
    if callable(o):
        return as_binding(fn(o))
    cls = type(o)
    return Binding(Key(cls), const(o, cls))


def as_(k: ta.Any, p: ta.Any) -> Binding:
    return Binding(as_key(k), as_provider(p))


def in_(b: ta.Any, sc: Scope) -> Binding:
    return dc.replace(as_binding(b), scope=check.isinstance(sc, Scope))


def singleton(b: ta.Any) -> Binding:
    return in_(b, Singleton())
