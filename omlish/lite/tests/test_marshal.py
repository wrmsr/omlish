# ruff: noqa: PT009 UP006 UP007
import abc
import dataclasses as dc
import datetime
import enum
import json
import typing as ta
import unittest

from .. import marshal as msh


##


_DEBUG_PRINT = lambda *a: None  # noqa
# _DEBUG_PRINT = print


class AbstractTestMarshal(unittest.TestCase):
    def _assert_marshal(self, a):
        if isinstance(a, tuple):
            v, ty = a
        else:
            v, ty = a, type(a)

        _DEBUG_PRINT((v, ty))

        m = msh.marshal_obj(v, ty)
        _DEBUG_PRINT(m)

        s = json.dumps(m)
        _DEBUG_PRINT(m)

        x = json.loads(s)
        _DEBUG_PRINT(x)

        u = msh.unmarshal_obj(x, ty)  # type: ignore
        _DEBUG_PRINT(u)

        self.assertEqual(u, v)
        _DEBUG_PRINT()


##


class TestMarshalSimple(AbstractTestMarshal):
    def test_marshal_simple(self):
        for a in [
            5,
            5.,
            'abc',
            b'abc',
            bytearray(b'abc'),
        ]:
            self._assert_marshal(a)

    def test_marshal_collections(self):
        for a in [
            [1, '2'],
            {1, 2},
            {'a': {'b': 3}},
        ]:
            self._assert_marshal(a)

    def test_marshal_datetimes(self):
        for a in [
            datetime.date.today(),  # noqa
            datetime.datetime.now(),  # noqa
            datetime.datetime.now().time(),  # noqa
        ]:
            self._assert_marshal(a)

    def test_marshal_generics(self):
        for a in [
            ({1: 2}, ta.Dict[int, int]),
            (1, ta.Optional[int]),
            (None, ta.Optional[int]),
        ]:
            self._assert_marshal(a)


##


@dc.dataclass
class Foo:
    i: int = 42
    dt: datetime.datetime = dc.field(default_factory=datetime.datetime.now)


@dc.dataclass
class Bar:
    l: ta.List[Foo]
    d: ta.Dict[str, Foo]
    i: int = 24


class TestMarshalDataclasses(AbstractTestMarshal):
    def test_marshal_dataclasses(self):
        for a in [
            Foo(),
            Bar([Foo(), Foo(i=11)], {'barf': Foo(i=-1)}),
        ]:
            self._assert_marshal(a)

    def test_strictness(self):
        u: Foo = msh.unmarshal_obj(dict(i=24), Foo)
        assert isinstance(u, Foo)
        assert u.i == 24

        with self.assertRaises(KeyError):  # noqa
            msh.unmarshal_obj(dict(i=24, j=25), Foo)

        m = dc.replace(msh.get_obj_marshaler(Foo), non_strict=True)  # type: ignore
        u = m.unmarshal(
            dict(i=24, j=25),
            msh.ObjMarshalContext(
                options=msh.ObjMarshalOptions(),
                manager=msh.OBJ_MARSHALER_MANAGER,
            ),
        )
        assert isinstance(u, Foo)
        assert u.i == 24

    def test_name_overrides(self):
        @dc.dataclass
        class Junk:
            a: str
            b: str = dc.field(metadata={msh.OBJ_MARSHALER_FIELD_KEY: 'b!'})
            c: str = dc.field(default='default c', metadata={msh.OBJ_MARSHALER_FIELD_KEY: None})

        j = Junk('a', 'b', 'c')
        m = msh.marshal_obj(j)
        self.assertEqual(m, {'a': 'a', 'b!': 'b'})

        u: Junk = msh.unmarshal_obj(m, Junk)
        self.assertEqual(u, Junk('a', 'b', 'default c'))


##


class Poly(abc.ABC):  # noqa
    pass


@dc.dataclass
class PolyA(Poly):
    a: str


@dc.dataclass
class PolyB(PolyA):
    b: str


@dc.dataclass
class PolyC(Poly):
    c: str


@dc.dataclass
class PolyD(PolyA, abc.ABC):
    d: str


@dc.dataclass
class PolyE(PolyD):
    e: str


@dc.dataclass
class PolyF(PolyD):
    f: str


#


class Node(abc.ABC):  # noqa
    pass


@dc.dataclass
class ValueNode(Node):
    v: ta.Any


@dc.dataclass
class OpNode(Node):
    op: str
    args: ta.List[Node]


class TestMarshalPolymorphic(AbstractTestMarshal):
    def test_polymorphic(self):
        for a in [
            PolyA('a'),
            (PolyA('a'), Poly),

            (ValueNode(5), Node),
            (OpNode('+', [OpNode('*', [ValueNode(2), ValueNode(3)]), ValueNode(5)]), Node),
        ]:
            self._assert_marshal(a)


##


class FooEnum(enum.Enum):
    X = enum.auto()
    Y = enum.auto()
    Z = enum.auto()


class TestMarshalEnum(AbstractTestMarshal):
    def test_polymorphic(self):
        for st in [
            FooEnum.X,
        ]:
            self._assert_marshal(*(st if isinstance(st, tuple) else (st,)))


##


class FooNamedTuple(ta.NamedTuple):
    x: int


class NamedTupleTest(AbstractTestMarshal):
    def test_namedtuple(self):
        self._assert_marshal((FooNamedTuple(420), FooNamedTuple))


##


FooLiteral = ta.Literal['a', 'b', 'c']


class TestMarshalLiterals(AbstractTestMarshal):
    def test_literal(self):
        self._assert_marshal(('b', FooLiteral))
