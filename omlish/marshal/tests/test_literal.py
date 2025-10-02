import typing as ta

from ... import check
from ... import reflect as rfl
from ..base.configs import ConfigRegistry
from ..base.contexts import MarshalContext
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalContext
from ..base.contexts import UnmarshalFactoryContext
from ..standard import new_standard_marshaler_factory
from ..standard import new_standard_unmarshaler_factory


Foo: ta.TypeAlias = ta.Literal['a', 'b', 'c']


def test_literal():
    r = ConfigRegistry()

    mf = new_standard_marshaler_factory()
    mfc = MarshalFactoryContext(config_registry=r, marshaler_factory=mf)
    mc = MarshalContext(config_registry=r, marshal_factory_context=mfc)
    assert check.not_none(mf.make_marshaler(mfc, rfl.type_(Foo)))().marshal(mc, 'a') == 'a'

    uf = new_standard_unmarshaler_factory()
    ufc = UnmarshalFactoryContext(config_registry=r, unmarshaler_factory=uf)
    uc = UnmarshalContext(config_registry=r, unmarshal_factory_context=ufc)
    assert check.not_none(uf.make_unmarshaler(ufc, rfl.type_(Foo)))().unmarshal(uc, 'a') == 'a'
