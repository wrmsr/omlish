# ruff: noqa: PT009 UP006 UP007
import abc
import dataclasses as dc
import datetime
import json
import typing as ta
import unittest

from .. import marshal as msh


##


_DEBUG_PRINT = lambda *a: None  # noqa
# _DEBUG_PRINT = print


class AbstractTestMarshal(unittest.TestCase):
    def _assert_marshal(self, v, ty=None):
        if ty is None:
            ty = type(v)

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
        for st in [
            5,
            5.,
            'abc',
            b'abc',
            bytearray(b'abc'),
            datetime.datetime.now(),  # noqa
            [1, '2'],
            {1, 2},
            {'a': {'b': 3}},
            ({1: 2}, ta.Dict[int, int]),
            (1, ta.Optional[int]),
            (None, ta.Optional[int]),
        ]:
            self._assert_marshal(*(st if isinstance(st, tuple) else (st,)))


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
        for o in [
            Foo(),
            Bar([Foo(), Foo(i=11)], {'barf': Foo(i=-1)}),
        ]:
            self._assert_marshal(o)


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
        for st in [
            PolyA('a'),
            (PolyA('a'), Poly),

            (ValueNode(5), Node),
            (OpNode('+', [OpNode('*', [ValueNode(2), ValueNode(3)]), ValueNode(5)]), Node),
        ]:
            self._assert_marshal(*(st if isinstance(st, tuple) else (st,)))
