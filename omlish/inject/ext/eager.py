import typing as ta

from ..bindings import as_
from ..keys import array
from ..keys import as_key
from ..types import Binding
from ..types import Bindings
from ..types import Injector
from ..types import Key


class _Eager(ta.NamedTuple):
    key: Key


_EAGER_ARRAY_KEY = array(_Eager)


def eager(arg: ta.Any) -> Binding:
    return as_(_EAGER_ARRAY_KEY, _Eager(as_key(arg)))


def create_eager_injector(nxt: ta.Callable[[Bindings], Injector], bs: Bindings) -> Injector:
    i = nxt(bs)
    if (eags := i.try_provide(_EAGER_ARRAY_KEY)).present:
        for e in eags.must():
            i.provide(e.key)
    return i


