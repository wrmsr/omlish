import dataclasses as dc
import typing as ta

from ..bindings import as_
from ..keys import as_key
from ..keys import multi
from ..providers import const
from ..types import Binding
from ..types import Bindings
from ..types import Injector
from ..types import Key


@dc.dataclass(frozen=True)
class _Eager:
    key: Key


_EAGER_MULTI_KEY = multi(_Eager)


def eager(arg: ta.Any) -> Binding:
    return as_(_EAGER_MULTI_KEY, const([_Eager(as_key(arg))]))


def create_eager_injector(nxt: ta.Callable[[Bindings], Injector], bs: Bindings) -> Injector:
    i = nxt(bs)
    if (eags := i.try_provide(_EAGER_MULTI_KEY)).present:
        for e in eags.must():
            i.provide(e.key)
    return i
