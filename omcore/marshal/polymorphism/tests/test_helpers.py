import dataclasses as dc

from ...api.configs import ConfigRegistry
from ...api.contexts import MarshalContext
from ...api.contexts import MarshalFactoryContext
from ...api.contexts import UnmarshalContext
from ...api.contexts import UnmarshalFactoryContext
from ...api.types import MarshalerFactory
from ...api.types import UnmarshalerFactory
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
from ..api import set_polymorphic_from_subclasses
from ..metadata import make_polymorphism_metadata_factories


@set_polymorphic_from_subclasses()
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


def test_polymorphism_helper():
    for _ in range(3):
        pmf, puf = make_polymorphism_metadata_factories()

        mf: MarshalerFactory = TypeCacheMarshalerFactory(
            RecursiveMarshalerFactory(
                MultiMarshalerFactory(
                    pmf,
                    DataclassMarshalerFactory(),
                    PRIMITIVE_MARSHALER_FACTORY,
                ),
            ),
        )

        uf: UnmarshalerFactory = TypeCacheUnmarshalerFactory(
            RecursiveUnmarshalerFactory(
                MultiUnmarshalerFactory(
                    puf,
                    DataclassUnmarshalerFactory(),
                    PRIMITIVE_UNMARSHALER_FACTORY,
                ),
            ),
        )

        o = PS2('0', PS1('1', 420))

        reg = ConfigRegistry()

        for _ in range(3):
            mfc = MarshalFactoryContext(configs=reg, marshaler_factory=mf)
            mc = MarshalContext(marshal_factory_context=mfc)
            v = mfc.make_marshaler(PB).marshal(mc, o)
            print(v)

            ufc = UnmarshalFactoryContext(configs=reg, unmarshaler_factory=uf)
            uc = UnmarshalContext(unmarshal_factory_context=ufc)
            o2 = ufc.make_unmarshaler(PB).unmarshal(uc, v)
            print(o2)

            assert o2 == o
