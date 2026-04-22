import typing as ta

import pytest

from ...api.contexts import MarshalContext
from ...api.errors import UnhandledTypeError
from ...api.types import Marshaler
from ...api.types import SimpleMarshaling
from ...api.values import Value
from ...singular.primitives import PRIMITIVE_MARSHALER_FACTORY
from ..api import Override
from ..override import OverrideMarshalerFactory


class IncIntMarshaler(Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return o + 1


class MyInt(int):
    pass


def test_override():
    msh = SimpleMarshaling(
        marshaler_factory=OverrideMarshalerFactory(PRIMITIVE_MARSHALER_FACTORY),
    )
    msh.get_config_registry().register(int, Override(marshaler=IncIntMarshaler()))
    assert msh.marshal('1') == '1'
    assert msh.marshal(1) == 2
    assert msh.marshal(False) is False
    with pytest.raises(UnhandledTypeError):
        msh.marshal(MyInt(1))
