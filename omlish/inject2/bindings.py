import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .multis import multi_provider
from .exceptions import DuplicateKeyException
from .keys import as_key
from .providers import ConstProvider
from .providers import Provider
from .providers import as_provider
from .providers import ctor as ctor_provider
from .providers import fn as fn_provider
from .types import Binding
from .types import Bindings
from .types import Key
from .types import _BindingGen
from .types import _ProviderGen


##


def as_binding(o: ta.Any) -> Binding:
    check.not_none(o)
    check.not_isinstance(o, (Element, Elements))
    if isinstance(o, Binding):
        return o
    if isinstance(o, Provider):
        return Binding(Key(o.provided_cls(lambda _: lang.raise_(TypeError(o)))), o)  # noqa
    if isinstance(o, type):
        return as_binding(ctor_provider(o))
    if callable(o):
        return as_binding(fn_provider(o))
    cls = type(o)
    return Binding(Key(cls), ConstProvider(cls, o))


def as_bindings(it: ta.Iterable[ta.Any]) -> ta.Sequence[Binding]:
    bs: list[Binding] = []
    for a in it:
        if a is not None:
            bs.append(as_binding(a))
    return bs


def as_(k: ta.Any, p: ta.Any) -> Binding:
    return Binding(as_key(k), as_provider(p))


##


def bind(*args: ta.Any) -> Bindings:
    bs: list[Binding] = []
    ps: list[Bindings] = []
    for a in args:
        if isinstance(a, Bindings):
            ps.append(a)
        elif a is not None:
            bs.append(as_binding(a))
    # This will contain a stacktrace, so no unnesting.
    return _Bindings(bs=bs, ps=ps)
