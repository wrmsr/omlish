import abc
import dataclasses as dc
import pickle  # noqa
import typing as ta

import pytest

from .. import api as api_
from .. import kwargs as kwargs_
from .. import metaclass as metaclass_
from .. import pickling as pickling_  # noqa
from .. import types as types_
from ... import lang


T = ta.TypeVar('T')


def test_meta():
    class Point(metaclass_.Data):
        x: int
        y: int

    pt = Point(1, 2)
    assert pt.x == 1
    pt.z = 2
    assert pt.z == 2

    class Abs(metaclass_.Data, abstract=True):
        x: int

    with pytest.raises(TypeError):
        Abs(1)

    class NAbs(Abs):
        pass

    assert NAbs(2).x == 2

    class AbsV(metaclass_.Data, abstract=True):
        @abc.abstractproperty
        def value(self) -> int:
            raise NotImplementedError

        @abc.abstractmethod
        def f(self):
            raise NotImplementedError

    class ImplV(AbsV):
        value: int

        def f(self):
            return 2

    assert ImplV(3).value == 3

    class ImplVNoF(AbsV, lang.Abstract):
        value: int

    with pytest.raises(TypeError):
        ImplVNoF(4)

    class Iface(metaclass_.Data, abstract=True, sealed=True, pickle=True):
        x: int

    with pytest.raises(TypeError):
        Iface(1)

    class Impl(Iface, final=True):
        y: int

    pt = Impl(1, 2)
    assert pt.x == 1
    pt.y = 2
    assert pt.y == 2
    pt.z = 3
    assert pt.z == 3

    class PackageIface(metaclass_.Data, abstract=True, sealed='package', pickle=True):  # noqa
        x: int

    class PackageIface2(PackageIface, abstract=True):  # noqa
        x: int

    class FrozenIface(metaclass_.Data, abstract=True, sealed=True, pickle=True, frozen=True):
        x: int

    class FrozenImpl(FrozenIface, final=True, frozen=True):
        y: int

    pt = FrozenImpl(1, 2)
    assert pt.x == 1
    with pytest.raises(dc.FrozenInstanceError):
        pt.y = 2

    with pytest.raises(TypeError):
        class Iface(Impl):
            pass

    with pytest.raises(TypeError):
        class Impl2(Impl):
            pass

    class Abs(metaclass_.Data, abstract=True):
        x: int

        @abc.abstractproperty
        def y(self) -> int:
            raise NotImplementedError

    with pytest.raises(TypeError):
        Abs(1)

    class AbsImpl(Iface, final=True):
        y: int

    pt = AbsImpl(1, 2)
    assert pt.x == 1
    pt.z = 2
    assert pt.z == 2

    with pytest.raises(TypeError):
        class AbsImpl2(Abs, final=True):
            pass

    class Gen(metaclass_.Data, ta.Generic[T]):
        val: T

    assert Gen(1).val == 1


def test_post_init():
    class Point(metaclass_.Data):
        x: int
        y: int

        api_.post_init(lambda pt: l.append(pt))

    l = []
    Point(1, 2)
    Point(3, 4)
    assert len(l) == 2


def test_generic():
    class Box(metaclass_.Data, ta.Generic[T]):
        value: T

    assert isinstance(Box(1), Box)
    # assert issubclass(Box[int], Box)

    class SubBox(Box):
        pass

    assert SubBox(1).value == 1

    class SubIntBox(Box[int]):
        pass

    assert SubIntBox(1).value == 1


def test_frozen():
    class Pt(metaclass_.Frozen):
        x: int
        y: int

    pt = Pt(1, 2)
    assert pt.x == 1
    assert pt.y == 2

    with pytest.raises(Exception):
        pt.x = 3

    class Pt2(Pt):
        z: int

    pt2 = Pt2(1, 2, 3)
    assert pt2.x == 1
    assert pt2.y == 2
    assert pt2.z == 3

    with pytest.raises(Exception):
        pt2.x = 3


def test_pure():
    class Pt(metaclass_.Pure):
        x: int
        y: int

    pt = Pt(1, 2)
    assert pt.x == 1
    assert pt.y == 2

    with pytest.raises(Exception):
        pt.x = 3

    with pytest.raises(Exception):
        class Pt2(Pt):
            pass


def test_confer():
    def _confer_enum_final(att, sub, sup, bases):
        return sub['abstract'] is dc.MISSING or not sub['abstract']

    class A(
        metaclass_.Data,
        abstract=True,
        confer={
            'final': types_.Conferrer(_confer_enum_final),
            'confer': types_.SUPER,
        }
    ):
        pass

    class B(A):
        pass

    with pytest.raises(Exception):
        class B_(B):
            pass

    class C(A, abstract=True):
        pass

    class D(C):
        pass

    with pytest.raises(Exception):
        class D_(D):
            pass


def test_slots():
    class C(metaclass_.Frozen, slots=True):
        x: int = 0

    c = C(1)
    assert c.x == 1
    with pytest.raises(Exception):
        c.y = 2

    class D(C, slots=True):
        y: int = 0

    d = D(1, 2)
    assert d.x == 1
    assert d.y == 2
    with pytest.raises(Exception):
        d.z = 3


class TestTuples:

    def test_tuple(self):
        class C(metaclass_.Tuple):
            x: int
            y: int

        c = C(1, 2)
        assert isinstance(c, tuple)
        assert c.x == 1
        assert c.y == 2
        with pytest.raises(Exception):
            c.a = 4

        class D(C):
            z: int

        d = D(1, 2, 3)
        assert isinstance(d, tuple)
        assert d.x == 1
        assert d.y == 2
        assert d.z == 3
        with pytest.raises(Exception):
            d.a = 4


def test_ident_eq():
    class C(metaclass_.Pure, eq=False):
        x: int

    assert C(1) != C(1)


def test_meta_class_md_kw():
    @api_.dataclass()
    class TestKw:
        o: ta.Any

    with pytest.raises(Exception):
        class C(metaclass_.Pure, _test_mc_kw=420):  # noqa
            f: int

    @kwargs_.register_class_metadata_kwarg_handler('_test_mc_kw')
    def _handle_test_mc_kw(cls, o):
        return TestKw(o)

    class C(metaclass_.Pure, _test_mc_kw=420):  # noqa
        f: int

    assert api_.metadatas_dict(C)[TestKw].o == 420
