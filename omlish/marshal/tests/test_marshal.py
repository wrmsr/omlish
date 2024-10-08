import dataclasses as dc
import datetime
import decimal
import enum
import fractions
import typing as ta

from ..base import MarshalContext
from ..base import UnmarshalContext
from ..registries import Registry
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

    reg: Registry = Registry()

    print()

    obj = Foo([420, 421], 'barf', Foo([1, 2], 'xxx', e=E.Y))
    print(obj)
    print()

    mc = MarshalContext(registry=reg, factory=mf)
    for _ in range(2):
        mobj = mc.make(type(obj)).marshal(mc, obj)
        print(mobj)
    print()

    uf = new_standard_unmarshaler_factory()

    uc = UnmarshalContext(registry=reg, factory=uf)
    for _ in range(2):
        uobj = uc.make(type(obj)).unmarshal(uc, mobj)  # noqa
        print(uobj)
    print()

    print(uc.make(ta.Any).unmarshal(uc, 420))
