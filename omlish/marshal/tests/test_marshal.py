import dataclasses as dc
import datetime
import decimal
import enum
import fractions
import typing as ta

from ..api.configs import ConfigRegistry
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..standard import new_standard_marshaler_factory
from ..standard import new_standard_unmarshaler_factory
from .foox import Foox


class E(enum.Enum):
    X = enum.auto()
    Y = enum.auto()
    Z = enum.auto()


@dc.dataclass(frozen=True)
class Foo(Foox):
    s: str
    f: ta.Optional['Foo'] = None
    e: E | None = None
    frac: fractions.Fraction = fractions.Fraction(1, 9)
    dec: decimal.Decimal = decimal.Decimal('3.140000000000000124344978758017532527446746826171875')
    dt: datetime.datetime = dc.field(default_factory=datetime.datetime.now)
    d: datetime.date = dc.field(default_factory=lambda: datetime.datetime.now().date())  # noqa
    t: datetime.time = dc.field(default_factory=lambda: datetime.datetime.now().time())  # noqa


def test_marshal():
    # reg = Registry()
    # reg.register(spec_of(int), SetType(marshaler=PrimitiveMarshaler()))

    mf = new_standard_marshaler_factory()

    reg = ConfigRegistry()

    print()

    obj = Foo([420, 421], 'barf', Foo([1, 2], 'xxx', e=E.Y))
    print(obj)
    print()

    mfc = MarshalFactoryContext(configs=reg, marshaler_factory=mf)
    mc = MarshalContext(configs=reg, marshal_factory_context=mfc)
    for _ in range(2):
        mobj = mfc.make_marshaler(type(obj)).marshal(mc, obj)
        print(mobj)
    print()

    uf = new_standard_unmarshaler_factory()

    ufc = UnmarshalFactoryContext(configs=reg, unmarshaler_factory=uf)
    uc = UnmarshalContext(configs=reg, unmarshal_factory_context=ufc)
    for _ in range(2):
        uobj = ufc.make_unmarshaler(type(obj)).unmarshal(uc, mobj)  # noqa
        print(uobj)
    print()

    print(ufc.make_unmarshaler(ta.Any).unmarshal(uc, 420))
