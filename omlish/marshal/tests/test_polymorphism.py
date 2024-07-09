import dataclasses as dc

from .. import polymorphism as poly
from ..base import MarshalContext
from ..base import MarshalerFactory
from ..base import RecursiveMarshalerFactory
from ..base import RecursiveUnmarshalerFactory
from ..base import UnmarshalContext
from ..base import UnmarshalerFactory
from ..dataclasses import DataclassMarshalerFactory
from ..dataclasses import DataclassUnmarshalerFactory
from ..factories import CompositeFactory
from ..factories import TypeCacheFactory
from ..polymorphism import PolymorphismMarshalerFactory
from ..polymorphism import PolymorphismUnmarshalerFactory
from ..primitives import PRIMITIVE_MARSHALER_FACTORY
from ..primitives import PRIMITIVE_UNMARSHALER_FACTORY
from ..registries import Registry


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


def test_polymorphism():
    p = poly.Polymorphism(
        PB,
        [
            poly.Impl(PS0, 's0'),
            poly.Impl(PS1, 's1'),
            poly.Impl(PS2, 's2'),
        ],
    )

    mf: MarshalerFactory = TypeCacheFactory(
        RecursiveMarshalerFactory(
            CompositeFactory(
                PolymorphismMarshalerFactory(p),
                DataclassMarshalerFactory(),
                PRIMITIVE_MARSHALER_FACTORY,
            ),
        ),
    )

    uf: UnmarshalerFactory = TypeCacheFactory(
        RecursiveUnmarshalerFactory(
            CompositeFactory(
                PolymorphismUnmarshalerFactory(p),
                DataclassUnmarshalerFactory(),
                PRIMITIVE_UNMARSHALER_FACTORY,
            ),
        ),
    )

    o = PS2('0', PS1('1', 420))

    reg = Registry()

    mc = MarshalContext(registry=reg, factory=mf)
    v = mc.make(PB).marshal(mc, o)
    print(v)

    uc = UnmarshalContext(registry=reg, factory=uf)
    o2 = uc.make(PB).unmarshal(uc, v)
    print(o2)
