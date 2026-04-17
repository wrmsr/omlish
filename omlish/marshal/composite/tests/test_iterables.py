import typing as ta

from ...api.contexts import UnmarshalContext
from ...api.contexts import UnmarshalFactoryContext
from ...api.options import Options
from ...standard.factories import StandardUnmarshalerFactory
from ..api import DefaultIterableConstructors


def test_ctor_option():
    uf = StandardUnmarshalerFactory()
    ufc = UnmarshalFactoryContext(unmarshaler_factory=uf)

    uc = UnmarshalContext(unmarshal_factory_context=ufc)
    u = ufc.make_unmarshaler(ta.Sequence[int]).unmarshal(uc, [1, 2, 3])
    assert u == (1, 2, 3)

    uc = UnmarshalContext(unmarshal_factory_context=ufc, options=Options([
        DefaultIterableConstructors(sequence=list),
    ]))
    u = ufc.make_unmarshaler(ta.Sequence[int]).unmarshal(uc, [1, 2, 3])
    assert u == [1, 2, 3]
