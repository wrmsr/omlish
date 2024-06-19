import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Elements
from .exceptions import DuplicateKeyException
from .keys import as_key
from .multis import multi_provider
from .providers import ConstProvider
from .providers import Provider
from .providers import as_provider
from .providers import ctor as ctor_provider
from .providers import fn as fn_provider
from .types import Binding
from .types import Bindings
from .types import Element
from .types import Key
from .types import _BindingGen
from .types import _ProviderGen


@dc.dataclass(frozen=True, eq=False)
class OverriddenElements(Element):
    b: Elements
    o: Elements


def override(p: Bindings, *a: ta.Any) -> Bindings:
    m: dict[Key, Binding] = {}
    for b in bind(*a).bindings():
        if b.key in m:
            raise DuplicateKeyException(b.key)
        m[b.key] = b
    return _Overrides(p, m)
