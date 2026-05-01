import dataclasses as dc

import pytest

from ...api.errors import UnhandledTypeError
from ...api.types import SimpleMarshaling
from ...factories.multi import MultiMarshalerFactory
from ...factories.multi import MultiUnmarshalerFactory
from ...objects.dataclasses import DataclassMarshalerFactory
from ...objects.dataclasses import DataclassUnmarshalerFactory
from ...singular.primitives import PRIMITIVE_MARSHALER_FACTORY
from ...singular.primitives import PRIMITIVE_UNMARSHALER_FACTORY
from ..api import OpenPolymorphismImpl
from ..api import OpenPolymorphismOptions
from ..open import OpenPolymorphismMarshalerFactory
from ..open import OpenPolymorphismUnmarshalerFactory


class Foo:
    pass


@dc.dataclass(frozen=True)
class IntFoo(Foo):
    i: int


@dc.dataclass(frozen=True)
class StrFoo(Foo):
    s: str


@dc.dataclass(frozen=True)
class BoolFoo(Foo):
    b: bool


def test_open():
    msh = SimpleMarshaling(
        marshaler_factory=MultiMarshalerFactory(
            OpenPolymorphismMarshalerFactory(Foo, opo := OpenPolymorphismOptions(
                strip_suffix=True,
            )),
            DataclassMarshalerFactory(),
            PRIMITIVE_MARSHALER_FACTORY,
        ),
        unmarshaler_factory=MultiUnmarshalerFactory(
            OpenPolymorphismUnmarshalerFactory(Foo, opo),
            DataclassUnmarshalerFactory(),
            PRIMITIVE_UNMARSHALER_FACTORY,
        ),
    )

    assert msh.marshal(420) == 420

    msh.config_registry.update(
        Foo,
        OpenPolymorphismImpl(IntFoo),
        OpenPolymorphismImpl(StrFoo),
    )

    assert (mv := msh.marshal(IntFoo(420), Foo)) == {'int': {'i': 420}}
    assert msh.unmarshal(mv, Foo) == IntFoo(420)
    assert (mv := msh.marshal(StrFoo('420'), Foo)) == {'str': {'s': '420'}}
    assert msh.unmarshal(mv, Foo) == StrFoo('420')

    with pytest.raises(UnhandledTypeError):
        msh.marshal(BoolFoo(True))

    msh.config_registry.update(
        Foo,
        OpenPolymorphismImpl(BoolFoo),
    )

    assert (mv := msh.marshal(IntFoo(420), Foo)) == {'int': {'i': 420}}
    assert msh.unmarshal(mv, Foo) == IntFoo(420)
    assert (mv := msh.marshal(StrFoo('420'), Foo)) == {'str': {'s': '420'}}
    assert msh.unmarshal(mv, Foo) == StrFoo('420')
    assert (mv := msh.marshal(BoolFoo(True), Foo)) == {'bool': {'b': True}}
    assert msh.unmarshal(mv, Foo) == BoolFoo(True)
