import dataclasses as dc
import enum
import typing as ta

from .. import polymorphism as poly
from ..base import MarshalContext
from ..base import UnmarshalContext
from ..global_ import marshal
from ..global_ import unmarshal
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
    e: ta.Optional[E] = None


def test_marshal():
    # reg = Registry()
    # reg.register(spec_of(int), SetType(marshaler=PrimitiveMarshaler()))

    mf = new_standard_marshaler_factory()

    reg = Registry()

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
        uobj = uc.make(type(obj)).unmarshal(uc, mobj)
        print(uobj)
    print()

    print(uc.make(ta.Any).unmarshal(uc, 420))


def test_marshal2():
    print(marshal([4, 20]))


@dc.dataclass(frozen=True)
class PB:
    a: str


@dc.dataclass(frozen=True)
class PS0(PB):
    b: str


@dc.dataclass(frozen=True)
class PS1(PB):
    b: int


def test_polymorphism():
    p = poly.Polymorphism(
        PB,
        [
            poly.Impl(PS0, 's0'),
            poly.Impl(PS1, 's1'),
        ],
    )
