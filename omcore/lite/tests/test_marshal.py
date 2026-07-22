# ruff: noqa: PT009 PT027 UP006 UP007 UP036 UP045
import abc
import collections
import dataclasses as dc
import datetime
import enum
import json
import sys
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

        u = msh.unmarshal_obj(x, ty)
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
        self.assertIsInstance(u, Foo)
        self.assertEqual(u.i, 24)

        with self.assertRaises(KeyError):  # noqa
            msh.unmarshal_obj(dict(i=24, j=25), Foo)

        m = msh.FieldsObjMarshaler(
            Foo,
            msh.get_obj_marshaler(Foo).fs,  # type: ignore
            non_strict=True,
        )

        u = m.unmarshal(
            dict(i=24, j=25),
            msh.ObjMarshalContext(
                options=msh.ObjMarshalOptions(),
                manager=msh.OBJ_MARSHALER_MANAGER,
            ),
        )
        self.assertIsInstance(u, Foo)
        self.assertEqual(u.i, 24)

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

    def test_omit_if_none(self):
        @dc.dataclass
        class Junk:
            a: str
            b: ta.Optional[str]
            c: ta.Optional[str] = dc.field(metadata={msh.OBJ_MARSHALER_OMIT_IF_NONE: True})

        self.assertEqual(msh.marshal_obj(Junk('a', 'b', 'c')), {'a': 'a', 'b': 'b', 'c': 'c'})
        self.assertEqual(msh.marshal_obj(Junk('a', None, None)), {'a': 'a', 'b': None})


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
OptFooLiteral = ta.Literal['a', 'b', 'c', None]


class TestMarshalLiterals(AbstractTestMarshal):
    def test_literal(self):
        self._assert_marshal(('b', FooLiteral))
        self._assert_marshal(('b', OptFooLiteral))
        self._assert_marshal((None, OptFooLiteral))


##


class TestInnerClassPoly(AbstractTestMarshal):
    @dc.dataclass(frozen=True)
    class NewCiManifest:
        @dc.dataclass(frozen=True)
        class Route:
            paths: ta.Sequence[str]

            content_type: str
            content_length: int

            @dc.dataclass(frozen=True)
            class Target(abc.ABC):  # noqa
                pass

            @dc.dataclass(frozen=True)
            class BytesTarget(Target):
                data: bytes

            @dc.dataclass(frozen=True)
            class CacheKeyTarget(Target):
                key: str

            target: Target

        routes: ta.Sequence[Route]

    def test_inner_class_ply(self):
        manifest = self.NewCiManifest(
            routes=[
                self.NewCiManifest.Route(
                    paths=['a', 'b'],
                    content_type='text/plain',
                    content_length=4,
                    target=self.NewCiManifest.Route.BytesTarget(b'abcd'),
                ),
                self.NewCiManifest.Route(
                    paths=['c', 'd'],
                    content_type='text/plain',
                    content_length=4,
                    target=self.NewCiManifest.Route.CacheKeyTarget('efgh'),
                ),
            ],
        )

        m = msh.marshal_obj(manifest)

        x = {
            'routes': [
                {
                    'content_length': 4,
                    'content_type': 'text/plain',
                    'paths': ['a', 'b'],
                    'target': {'bytes': {'data': 'YWJjZA=='}},
                },
                {
                    'content_length': 4,
                    'content_type': 'text/plain',
                    'paths': ['c', 'd'],
                    'target': {'cache_key': {'key': 'efgh'}},
                },
            ],
        }

        self.assertEqual(m, x)


##


class TestUnions(AbstractTestMarshal):
    def test_unions(self):
        self._assert_marshal((420, ta.Union[int, str]))
        self._assert_marshal(('420', ta.Union[int, str]))

        if sys.version_info >= (3, 10):
            self._assert_marshal((420, int | str))
            self._assert_marshal(('420', int | str))

        #

        self._assert_marshal((420, ta.Union[int, str, None]))
        self._assert_marshal(('420', ta.Union[int, str, None]))
        self._assert_marshal((None, ta.Union[int, str, None]))

        self._assert_marshal((420, ta.Optional[ta.Union[int, str]]))
        self._assert_marshal(('420', ta.Optional[ta.Union[int, str]]))
        self._assert_marshal((None, ta.Optional[ta.Union[int, str]]))

        if sys.version_info >= (3, 10):
            self._assert_marshal((420, int | str | None))
            self._assert_marshal(('420', int | str | None))
            self._assert_marshal((None, int | str | None))

        #

        self._assert_marshal((('abc',), ta.Optional[ta.Sequence[str]]))
        self._assert_marshal((('a', 'b', 'c'), ta.Optional[ta.Sequence[str]]))
        self._assert_marshal((None, ta.Optional[ta.Sequence[str]]))

        if sys.version_info >= (3, 10):
            self._assert_marshal((('abc',), ta.Sequence[str] | None))
            self._assert_marshal((('a', 'b', 'c'), ta.Sequence[str] | None))
            self._assert_marshal((None, ta.Sequence[str] | None))

        #

        self._assert_marshal(('abc', ta.Union[str, ta.Sequence[str]]))
        self._assert_marshal((('abc',), ta.Union[str, ta.Sequence[str]]))
        self._assert_marshal((('a', 'b', 'c'), ta.Union[str, ta.Sequence[str]]))

        if sys.version_info >= (3, 10):
            self._assert_marshal(('abc', str | ta.Sequence[str]))
            self._assert_marshal((('abc',), str | ta.Sequence[str]))
            self._assert_marshal((('a', 'b', 'c'), str | ta.Sequence[str]))

        #

        self._assert_marshal(('abc', ta.Union[str, ta.Sequence[str], None]))
        self._assert_marshal((('abc',), ta.Union[str, ta.Sequence[str], None]))
        self._assert_marshal((('a', 'b', 'c'), ta.Union[str, ta.Sequence[str], None]))
        self._assert_marshal((None, ta.Union[str, ta.Sequence[str], None]))

        if sys.version_info >= (3, 10):
            self._assert_marshal(('abc', str | ta.Sequence[str]))
            self._assert_marshal((('abc',), str | ta.Sequence[str]))
            self._assert_marshal((('a', 'b', 'c'), str | ta.Sequence[str]))
            self._assert_marshal((None, str | ta.Sequence[str] | None))


##


@dc.dataclass
class NonInitFieldDc:
    x: int
    y: int = dc.field(default=0, init=False)


@dc.dataclass
class SimpleDc:
    x: int


UntypedNt = collections.namedtuple('UntypedNt', 'x y')  # noqa


class TypedNt(ta.NamedTuple):
    x: int
    y: str


class TestFieldsMarshaling(unittest.TestCase):
    def test_non_init_fields_roundtrip(self):
        # init=False fields are excluded from both directions - unmarshal passes every key as a ctor kwarg.
        o = NonInitFieldDc(1)
        m = msh.marshal_obj(o)
        self.assertEqual(m, {'x': 1})
        u: NonInitFieldDc = msh.unmarshal_obj(m, NonInitFieldDc)
        self.assertEqual(u, o)

    def test_marshaler_cache_keyed_by_kwargs(self):
        # strict first, then non-strict
        mgr = msh.ObjMarshalerManagerImpl()
        mgr.get_obj_marshaler(SimpleDc)
        ns = mgr.get_obj_marshaler(SimpleDc, non_strict_fields=True)
        self.assertEqual(ns.unmarshal({'x': 1, 'zzz': 2}, mgr.make_context(None)), SimpleDc(1))

        # non-strict first, then strict
        mgr = msh.ObjMarshalerManagerImpl()
        mgr.get_obj_marshaler(SimpleDc, non_strict_fields=True)
        st = mgr.get_obj_marshaler(SimpleDc)
        with self.assertRaises(KeyError):
            st.unmarshal({'x': 1, 'zzz': 2}, mgr.make_context(None))

    def test_untyped_namedtuple(self):
        o = UntypedNt(1, 'a')
        m = msh.marshal_obj(o)
        self.assertEqual(m, {'x': 1, 'y': 'a'})
        u: UntypedNt = msh.unmarshal_obj(m, UntypedNt)
        self.assertEqual(u, o)

    def test_typed_namedtuple(self):
        o = TypedNt(1, 'a')
        m = msh.marshal_obj(o)
        self.assertEqual(m, {'x': 1, 'y': 'a'})
        u: TypedNt = msh.unmarshal_obj(m, TypedNt)
        self.assertEqual(u, o)
