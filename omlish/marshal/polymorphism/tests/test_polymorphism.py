import dataclasses as dc

from ...base.configs import ConfigRegistry
from ...base.contexts import MarshalContext
from ...base.contexts import MarshalFactoryContext
from ...base.contexts import UnmarshalContext
from ...base.contexts import UnmarshalFactoryContext
from ...base.types import MarshalerFactory
from ...base.types import UnmarshalerFactory
from ...factories.multi import MultiMarshalerFactory
from ...factories.multi import MultiUnmarshalerFactory
from ...factories.recursive import RecursiveMarshalerFactory
from ...factories.recursive import RecursiveUnmarshalerFactory
from ...factories.typecache import TypeCacheMarshalerFactory
from ...factories.typecache import TypeCacheUnmarshalerFactory
from ...objects.dataclasses import DataclassMarshalerFactory
from ...objects.dataclasses import DataclassUnmarshalerFactory
from ...singular.primitives import PRIMITIVE_MARSHALER_FACTORY
from ...singular.primitives import PRIMITIVE_UNMARSHALER_FACTORY
from ..marshal import PolymorphismMarshalerFactory
from ..types import FieldTypeTagging
from ..types import Impl
from ..types import Polymorphism
from ..types import WrapperTypeTagging
from ..unmarshal import PolymorphismUnmarshalerFactory


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
            MultiMarshalerFactory(
                PolymorphismMarshalerFactory(P_POLYMORPHISM, tt),
                DataclassMarshalerFactory(),
                PRIMITIVE_MARSHALER_FACTORY,
            ),
        ),
    )

    uf: UnmarshalerFactory = TypeCacheUnmarshalerFactory(
        RecursiveUnmarshalerFactory(
            MultiUnmarshalerFactory(
                PolymorphismUnmarshalerFactory(P_POLYMORPHISM, tt),
                DataclassUnmarshalerFactory(),
                PRIMITIVE_UNMARSHALER_FACTORY,
            ),
        ),
    )

    o = PS2('0', PS1('1', 420))

    reg = ConfigRegistry()

    mfc = MarshalFactoryContext(configs=reg, marshaler_factory=mf)
    mc = MarshalContext(configs=reg, marshal_factory_context=mfc)
    v = mfc.make_marshaler(PB).marshal(mc, o)
    print(v)

    ufc = UnmarshalFactoryContext(configs=reg, unmarshaler_factory=uf)
    uc = UnmarshalContext(configs=reg, unmarshal_factory_context=ufc)
    o2 = ufc.make_unmarshaler(PB).unmarshal(uc, v)
    print(o2)


def test_polymorphism_wrapper():
    _test_polymorphism(WrapperTypeTagging())


def test_polymorphism_field():
    _test_polymorphism(FieldTypeTagging('$type'))
