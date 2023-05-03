import typing as ta

from .. import check
from .. import lang
from .providers import ConstProvider
from .providers import Provider
from .types import Binding
from .types import Bindings
from .types import Key
from .types import _BindingGen
from .types import _ProviderGen


def as_binding(o: ta.Any) -> Binding:
    check.not_none(o)
    # check.not_isinstance(o, Bindings)
    if isinstance(o, Binding):
        return o
    if isinstance(o, _BindingGen):
        return o.binding()
    if isinstance(o, Provider):
        return Binding(Key(o.provided_cls(lambda _: lang.raise_(TypeError(o)))), o)
    if isinstance(o, _ProviderGen):
        return as_binding(o.provider())
    cls = type(o)
    return Binding(Key(cls), ConstProvider(cls, o))


def as_bindings(*args: ta.Any) -> Bindings:
    bs: ta.List[Binding] = []
    for a in args:
        if a is not None:
            bs.append(as_binding(a))
    return bs


def bind(*args: ta.Any) -> Bindings:
    raise NotImplementedError


def build_provider_map(bs: Bindings) -> ta.Mapping[Key, Provider]:
    pm: ta.Dict[Key, Provider] = {}
    am: ta.Dict[Key, ta.List[Provider]] = {}
    for b in bs:
        if b.key.arr:
            am.setdefault(b.key, []).append(b.provider)
        else:
            if b.key in pm:
                raise KeyError(b.key)
            pm[b.key] = b.provider
    if am:
        raise NotImplementedError
    return pm
