import enum

from ...api.types import SimpleMarshaling
from ...factories.multi import MultiMarshalerFactory
from ...factories.multi import MultiUnmarshalerFactory
from ...singular.primitives import PRIMITIVE_MARSHALER_FACTORY
from ...singular.primitives import PRIMITIVE_UNMARSHALER_FACTORY
from ..enums import EnumMarshalerFactory
from ..enums import EnumMode
from ..enums import EnumUnmarshalerFactory


class FooEnum(enum.Enum):
    FOO = 'foo!'
    BAR = 'bar?'


def test_enum_name():
    msh = SimpleMarshaling(
        marshaler_factory=MultiMarshalerFactory(
            EnumMarshalerFactory(),
            PRIMITIVE_MARSHALER_FACTORY,
        ),
        unmarshaler_factory=MultiUnmarshalerFactory(
            EnumUnmarshalerFactory(),
            PRIMITIVE_UNMARSHALER_FACTORY,
        ),
    )

    assert msh.marshal(FooEnum.FOO) == 'FOO'
    assert msh.marshal(FooEnum.BAR) == 'BAR'
    assert msh.unmarshal('FOO', FooEnum) == FooEnum.FOO
    assert msh.unmarshal('BAR', FooEnum) == FooEnum.BAR


def test_enum_value():
    msh = SimpleMarshaling(
        marshaler_factory=MultiMarshalerFactory(
            EnumMarshalerFactory(EnumMode.VALUE),
            PRIMITIVE_MARSHALER_FACTORY,
        ),
        unmarshaler_factory=MultiUnmarshalerFactory(
            EnumUnmarshalerFactory(EnumMode.VALUE),
            PRIMITIVE_UNMARSHALER_FACTORY,
        ),
    )

    assert msh.marshal(FooEnum.FOO) == 'foo!'
    assert msh.marshal(FooEnum.BAR) == 'bar?'
    assert msh.unmarshal('foo!', FooEnum) == FooEnum.FOO
    assert msh.unmarshal('bar?', FooEnum) == FooEnum.BAR
