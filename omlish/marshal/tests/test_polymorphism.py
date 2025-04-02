import dataclasses as dc

from ..base import MarshalContext
from ..base import MarshalerFactory
from ..base import MultiMarshalerFactory
from ..base import MultiUnmarshalerFactory
from ..base import RecursiveMarshalerFactory
from ..base import RecursiveUnmarshalerFactory
from ..base import TypeCacheMarshalerFactory
from ..base import TypeCacheUnmarshalerFactory
from ..base import UnmarshalContext
from ..base import UnmarshalerFactory
from ..objects.dataclasses import DataclassMarshalerFactory
from ..objects.dataclasses import DataclassUnmarshalerFactory
from ..polymorphism.marshal import PolymorphismMarshalerFactory
from ..polymorphism.metadata import FieldTypeTagging
from ..polymorphism.metadata import Impl
from ..polymorphism.metadata import Polymorphism
from ..polymorphism.metadata import WrapperTypeTagging
from ..polymorphism.unmarshal import PolymorphismUnmarshalerFactory
from ..registries import Registry
from ..singular.primitives import PRIMITIVE_MARSHALER_FACTORY
from ..singular.primitives import PRIMITIVE_UNMARSHALER_FACTORY


@dc.dataclass(frozen=True)
class PB:
    a: str


@dc.dataclass(frozen=True)
class PS0(PB):
    b: str


@dc.dataclass(frozen=True)
class PS1(PB):
    b: int


@dc.dataclass(frozen=True)
class PS2(PB):
    b: PB


P_POLYMORPHISM = Polymorphism(
    PB,
    [
        Impl(PS0, 's0'),
        Impl(PS1, 's1'),
        Impl(PS2, 's2'),
    ],
)


def _test_polymorphism(tt):
    mf: MarshalerFactory = TypeCacheMarshalerFactory(
        RecursiveMarshalerFactory(
            MultiMarshalerFactory([
                PolymorphismMarshalerFactory(P_POLYMORPHISM, tt),
                DataclassMarshalerFactory(),
                PRIMITIVE_MARSHALER_FACTORY,
            ]),
        ),
    )

    uf: UnmarshalerFactory = TypeCacheUnmarshalerFactory(
        RecursiveUnmarshalerFactory(
            MultiUnmarshalerFactory([
                PolymorphismUnmarshalerFactory(P_POLYMORPHISM, tt),
                DataclassUnmarshalerFactory(),
                PRIMITIVE_UNMARSHALER_FACTORY,
            ]),
        ),
    )

    o = PS2('0', PS1('1', 420))

    reg: Registry = Registry()

    mc = MarshalContext(registry=reg, factory=mf)
    v = mc.make(PB).marshal(mc, o)
    print(v)

    uc = UnmarshalContext(registry=reg, factory=uf)
    o2 = uc.make(PB).unmarshal(uc, v)
    print(o2)


def test_polymorphism_wrapper():
    _test_polymorphism(WrapperTypeTagging())


def test_polymorphism_field():
    _test_polymorphism(FieldTypeTagging('$type'))
