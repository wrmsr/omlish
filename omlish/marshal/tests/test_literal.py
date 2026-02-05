import typing as ta

from ... import check
from ... import reflect as rfl
from ..api.configs import ConfigRegistry
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..standard import new_standard_marshaler_factory
from ..standard import new_standard_unmarshaler_factory


Foo: ta.TypeAlias = ta.Literal['a', 'b', 'c']


def test_literal():
    r = ConfigRegistry()

    mf = new_standard_marshaler_factory()
    mfc = MarshalFactoryContext(configs=r, marshaler_factory=mf)
    mc = MarshalContext(configs=r, marshal_factory_context=mfc)
    assert check.not_none(mf.make_marshaler(mfc, rfl.type_(Foo)))().marshal(mc, 'a') == 'a'

    uf = new_standard_unmarshaler_factory()
    ufc = UnmarshalFactoryContext(configs=r, unmarshaler_factory=uf)
    uc = UnmarshalContext(configs=r, unmarshal_factory_context=ufc)
    assert check.not_none(uf.make_unmarshaler(ufc, rfl.type_(Foo)))().unmarshal(uc, 'a') == 'a'
