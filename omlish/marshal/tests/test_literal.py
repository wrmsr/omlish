import typing as ta

from ... import reflect as rfl
from ..base import MarshalContext
from ..base import UnmarshalContext
from ..registries import Registry
from ..standard import new_standard_marshaler_factory
from ..standard import new_standard_unmarshaler_factory


Foo: ta.TypeAlias = ta.Literal['a', 'b', 'c']


def test_literal():
    r = Registry()

    mf = new_standard_marshaler_factory()
    mc = MarshalContext(r, factory=mf)
    assert mf(mc, rfl.type_(Foo)).marshal(mc, 'a') == 'a'

    uf = new_standard_unmarshaler_factory()
    uc = UnmarshalContext(r, factory=uf)
    assert uf(uc, rfl.type_(Foo)).unmarshal(uc, 'a') == 'a'
