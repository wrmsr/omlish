import abc
import copy
import dataclasses as _dc
import inspect
import pprint  # noqa
import typing as ta

import pytest

from omlish import cached
from omlish import lang
from omlish import reflect as rfl  # noqa

from ... import dataclasses as dc
from ..inspect import inspect_fields  # noqa


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


def test_simple():
    @dc.dataclass()
    class Foo:
        x: int
        y: int

    @_dc.dataclass()
    class Bar:
        x: int
        z: int

    @dc.dataclass()
    class Baz0(Foo, Bar):
        a: int

    @_dc.dataclass()
    class Baz1(Foo, Bar):
        a: int

    print(Foo(1, 2))


def test_validate_coerce():
    @dc.dataclass()
    class Bar:
        x: int = dc.xfield(coerce=int, validate=lambda x: x < 10)

    print(Bar(4))
    print(Bar('4'))  # type: ignore

    try:
        Bar(11)
    except dc.ValidationError as ve:  # noqa
        # assert __file__ in repr(ve)  # noqa
        pass
    else:
        raise Exception('should raise')  # noqa


def test_validate_init():
    @dc.dataclass()
    class C:
        x: int = dc.xfield(validate=lambda x: x > 10)

        dc.validate(lambda x: x < 20)

        @dc.validate  # noqa
        @staticmethod
        def _validate_x_not_15(x: int) -> bool:
            return x != 15

        @dc.init
        def _init_foo(self) -> None:
            self._foo = 100

    c = C(11)
    assert c._foo == 100  # noqa

    with pytest.raises(dc.ValidationError):
        C(9)


# def test_mcls():
#     class C(dc.Data):
#         x: int
#
#     assert C(10).x == 10


def test_reflect():
    @dc.dataclass()
    class Foo:
        x: int
        y: int

    @_dc.dataclass()
    class Bar:
        x: int
        z: int

    @dc.dataclass()
    class Baz0(Foo, Bar):
        a: int

    ref = dc.reflect(Baz0)
    print(ref)
    # print(ref.params)
    # print(ref.params_extras)
    # print(ref.merged_metadata)


def test_abc():
    class Abc(abc.ABC):
        def foo(self):
            return 'foo'

        @abc.abstractmethod
        def m(self):
            raise NotImplementedError

        @property
        @abc.abstractmethod
        def p(self):
            raise NotImplementedError

    class D0(Abc):
        pass
    with pytest.raises(TypeError):
        D0()  # type: ignore

    @dc.dataclass(frozen=True)
    class D1(Abc):
        def m(self):
            return 'm'

        p: str = dc.field(override=True)  # type: ignore

    d1 = D1('p')
    assert d1.p == 'p'
    assert d1.p == 'p'
    with pytest.raises(dc.FrozenInstanceError):
        d1.p = 'p2'  # type: ignore  # noqa
    assert d1.foo() == 'foo'

    @dc.dataclass()
    class D2(Abc):
        def m(self):
            return 'm'

        p: str = dc.field(override=True)  # type: ignore

    d2 = D2('p')
    assert d2.p == 'p'
    assert d2.p == 'p'
    d2.p = 'p2'
    assert d2.p == 'p2'

    ##

    class Abstract(lang.Abstract):
        def foo(self):
            return 'foo'

        @abc.abstractmethod
        def m(self):
            raise NotImplementedError

        @property
        @abc.abstractmethod
        def p(self):
            raise NotImplementedError

    with pytest.raises(TypeError):
        class D3(Abstract):
            pass

    @dc.dataclass(frozen=True)
    class D4(Abstract):
        def m(self):
            return 'm'

        p: str = dc.field(override=True)  # type: ignore

    d4 = D4('p')
    assert d4.p == 'p'
    assert d4.p == 'p'
    with pytest.raises(dc.FrozenInstanceError):
        d4.p = 'p2'  # type: ignore  # noqa
    assert d4.foo() == 'foo'

    @dc.dataclass()
    class D5(Abstract):
        def m(self):
            return 'm'

        p: str = dc.field(override=True)  # type: ignore

    d5 = D5('p')
    assert d5.p == 'p'
    assert d5.p == 'p'
    d5.p = 'p5'
    assert d5.p == 'p5'


def test_reorder():
    @dc.dataclass()
    class A:
        x: int
        y: int = 3

    @dc.dataclass(reorder=True)  # type: ignore
    class B(A):  # noqa
        z: int  # type: ignore

    b = B(1, 2)  # type: ignore
    assert b.x == 1
    assert b.z == 2
    assert b.y == 3


# def test_generics():
#     @dc.dataclass()
#     class Box(ta.Generic[T]):
#         v: T
#
#     rty0 = rfl.type_(Box[int])  # noqa
#
#     assert Box[int](5).v == 5
#
#     @dc.dataclass()
#     class IntBox(Box[int]):
#         pass
#
#     rty1 = rfl.type_(IntBox)  # noqa
#
#     assert IntBox(5).v == 5
#
#     ifs = inspect_fields(IntBox)
#     print(ifs.field_owners)


def test_generics2():
    @dc.dataclass(frozen=True, generic_init=True)  # type: ignore
    class Thing(ta.Generic[T]):
        s: set[T]
        # mk: ta.Mapping[K, T]
        # mv: ta.Mapping[T, V]
        # mfk: ta.Mapping[ta.FrozenSet[K], T]
        # mfv: ta.Mapping[T, ta.FrozenSet[V]]
        mk: ta.Mapping[str, T]
        mv: ta.Mapping[T, str]
        mfk: ta.Mapping[frozenset[str], T]
        mfv: ta.Mapping[T, frozenset[str]]

    print()

    pprint.pprint(dict(inspect.signature(Thing).parameters))

    @dc.dataclass(frozen=True, generic_init=True)  # type: ignore
    class IntThing(Thing[int]):
        pass

    pprint.pprint(dict(inspect.signature(IntThing).parameters))

    @dc.dataclass(frozen=True, generic_init=True)  # type: ignore
    class Thing2(Thing[K]):
        pass

    @dc.dataclass(frozen=True, generic_init=True)  # type: ignore
    class IntThing2(Thing2[int]):
        pass

    pprint.pprint(dict(inspect.signature(IntThing2).parameters))


# def test_confer_frozen():
#     class A(dc.Frozen):
#         x: int
#
#     with pytest.raises(AttributeError):
#         A(2).x = 3
#
#     class B(A):
#         y: int
#
#     with pytest.raises(AttributeError):
#         B(2, 3).x = 3


# def test_box():
#     class Thing(dc.Box[list[str]]):
#         pass
#
#     assert Thing('foo').v == 'foo'
#
#     sig = inspect.signature(Thing)
#
#     assert sig.parameters['v'].annotation == list[str]


def test_check_type():
    @dc.dataclass(frozen=True)
    class C:
        x: int = dc.field(check_type=True)  # type: ignore

    assert C(5).x == 5
    with pytest.raises(TypeError):
        C('5')  # type: ignore


class HashCounter:
    n = 0

    def __hash__(self):
        self.n += 1
        return id(self)


def test_cache_hash():
    @dc.dataclass(frozen=True)
    class NoCacheDc:
        c: HashCounter = dc.field(default_factory=HashCounter)

    o: ta.Any = NoCacheDc()
    assert o.c.n == 0
    hash(o)
    assert o.c.n == 1
    hash(o)
    assert o.c.n == 2

    @dc.dataclass(frozen=True, cache_hash=True)  # type: ignore
    class CacheDc:
        c: HashCounter = dc.field(default_factory=HashCounter)

    o = CacheDc()
    assert o.c.n == 0
    hash(o)
    assert o.c.n == 1
    hash(o)
    assert o.c.n == 1


def test_extra_params_deco():
    @dc.dataclass(frozen=True)
    @dc.extra_class_params(cache_hash=True)
    class CacheDc:
        c: HashCounter = dc.field(default_factory=HashCounter)

    o = CacheDc()
    hash(o)
    hash(o)
    assert o.c.n == 1


def test_mypy():
    @dc.dataclass(frozen=True)
    class Foo:
        i: int
        f: float = dc.field(default=1.)

    # Foo('hi')
    # Foo(1, 'hi')


def test_cached_property():
    c = 0

    @dc.dataclass(frozen=True)
    class Foo:
        x: int

        @cached.property
        def y(self) -> int:
            nonlocal c
            c += 1
            return self.x + 1

    f = Foo(3)
    assert f.x == 3
    assert c == 0
    for _ in range(2):
        assert f.y == 4
        assert c == 1
    with pytest.raises(dc.FrozenInstanceError):
        f.x = 5  # type: ignore  # noqa


def test_cached_init_property_outer_deco_BAD_DO_NOT_DO():  # noqa
    c = 0

    @dc.dataclass(frozen=True)
    class Foo:
        x: int

        # NOTE: BREAKS TYPECHECKING - mypy considers this Any afterward. don't do this.
        @dc.init  # type: ignore
        @cached.property
        def y(self) -> int:
            nonlocal c
            c += 1
            return self.x + 1

    f = Foo(3)
    assert c == 1
    assert f.x == 3
    for _ in range(2):
        assert f.y == 4
        assert c == 1
    with pytest.raises(dc.FrozenInstanceError):
        f.x = 5  # type: ignore  # noqa


def test_cached_init_property_inner_deco():
    c = 0

    @dc.dataclass(frozen=True)
    class Foo:
        x: int

        @cached.property
        @dc.init
        def y(self) -> int:
            nonlocal c
            c += 1
            return self.x + 1

    f = Foo(3)
    assert c == 1
    assert f.x == 3
    for _ in range(2):
        assert f.y == 4
        assert c == 1
    with pytest.raises(dc.FrozenInstanceError):
        f.x = 5  # type: ignore  # noqa


def test_repr_lambda():
    @dc.dataclass()
    class Foo:
        x: int
        y: str = dc.xfield(repr_fn=lambda y: y + '!')
        z: int = dc.xfield(repr_fn=lambda z: z if z > 0 else None)

    assert repr(Foo(2, 'hi', 3)).endswith('.Foo(x=2, y=hi!, z=3)')
    assert repr(Foo(1, 'bye', 0)).endswith('.Foo(x=1, y=bye!)')


def test_copy():
    @dc.dataclass()
    class Foo:
        x: int
        y: int

    f = Foo(1, 2)
    c = copy.copy(f)
    assert f == c
    assert f is not c


def test_default_factory_coerce():
    def coerce(x: int) -> int:
        return x * 2

    @dc.dataclass()
    class C:
        x: int = dc.xfield(coerce=coerce, default_factory=lambda: 2)

    assert C().x == 4
    assert C(3).x == 6
