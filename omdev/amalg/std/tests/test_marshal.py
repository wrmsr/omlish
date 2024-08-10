# ruff: noqa: PT009
import dataclasses as dc
import datetime
import json
import typing as ta
import unittest

from .. import marshal as msh


@dc.dataclass
class Foo:
    i: int = 42
    dt: datetime.datetime = dc.field(default_factory=datetime.datetime.now)


@dc.dataclass
class Bar:
    l: ta.List[Foo]
    d: ta.Dict[str, Foo]
    i: int = 24


class TestMarshal(unittest.TestCase):
    def test_marshal(self):
        for st in [
            5,
            5.,
            'abc',
            b'abc',
            bytearray(b'abc'),
            datetime.datetime.now(),
            [1, '2'],
            {1, 2},
            {'a': {'b': 3}},
            Foo(),
            ({1: 2}, ta.Dict[int, int]),
        ]:
            if isinstance(st, tuple):
                v, ty = st
            else:
                v, ty = st, type(st)

            print((v, ty))
            m = msh.marshal_obj(v)
            print(m)
            s = json.dumps(m)
            print(m)
            x = json.loads(s)
            print(x)
            u = msh.unmarshal_obj(x, ty)
            print(u)

            self.assertEqual(u, v)
            print()
