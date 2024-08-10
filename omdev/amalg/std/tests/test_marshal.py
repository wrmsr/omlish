# ruff: noqa: PT009
import datetime
import json
import unittest

from .. import marshal as msh


class TestMarshal(unittest.TestCase):
    def test_marshal(self):
        for st in [
            5,
            5.,
            'abc',
            b'abc',
            bytearray(b'abc'),
            datetime.datetime.now(),
        ]:
            if isinstance(st, tuple):
                o, ty = st
            else:
                o, ty = st, type(st)

            m = msh.marshal_obj(o)
            s = json.dumps(m)
            x = json.loads(s)
            u = msh.unmarshal_obj(x, ty)

            self.assertEqual(u, o)
