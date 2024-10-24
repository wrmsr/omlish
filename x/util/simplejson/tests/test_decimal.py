import decimal
import io
from unittest import TestCase

from ... import simplejson as json


class TestDecimal(TestCase):
    NUMS = '1.0', '10.00', '1.1', '1234567890.1234567890', '500'

    def dumps(self, obj, **kw):
        sio = io.StringIO()
        json.dump(obj, sio, **kw)
        res = json.dumps(obj, **kw)
        self.assertEqual(res, sio.getvalue())
        return res

    def loads(self, s, **kw):
        sio = io.StringIO(s)
        res = json.loads(s, **kw)
        self.assertEqual(res, json.load(sio, **kw))
        return res

    def test_decimal_encode(self):
        for d in map(decimal.Decimal, self.NUMS):
            self.assertEqual(self.dumps(d, use_decimal=True), str(d))

    def test_decimal_decode(self):
        for s in self.NUMS:
            self.assertEqual(
                self.loads(s, parse_float=decimal.Decimal), decimal.Decimal(s),
            )

    def test_stringify_key(self):
        for d in map(decimal.Decimal, self.NUMS):
            v = {d: d}
            self.assertEqual(
                self.loads(
                    self.dumps(v, use_decimal=True), parse_float=decimal.Decimal,
                ),
                {str(d): d},
            )

    def test_decimal_roundtrip(self):
        for d in map(decimal.Decimal, self.NUMS):
            # The type might not be the same (int and Decimal) but they
            # should still compare equal.
            for v in [d, [d], {'': d}]:
                self.assertEqual(
                    self.loads(
                        self.dumps(v, use_decimal=True), parse_float=decimal.Decimal,
                    ),
                    v,
                )

    def test_decimal_defaults(self):
        d = decimal.Decimal('1.1')
        # use_decimal=True is the default
        self.assertRaises(TypeError, json.dumps, d, use_decimal=False)
        self.assertEqual('1.1', json.dumps(d))
        self.assertEqual('1.1', json.dumps(d, use_decimal=True))
        self.assertRaises(TypeError, json.dump, d, io.StringIO(), use_decimal=False)
        sio = io.StringIO()
        json.dump(d, sio)
        self.assertEqual('1.1', sio.getvalue())
        sio = io.StringIO()
        json.dump(d, sio, use_decimal=True)
        self.assertEqual('1.1', sio.getvalue())

    # def test_decimal_reload(self):
    #     # Simulate a subinterpreter that reloads the Python modules but not
    #     # the C code https://github.com/simplejson/simplejson/issues/34
    #     global Decimal
    #     Decimal = reload_module(decimal).Decimal
    #     import simplejson.encoder
    #
    #     simplejson.encoder.Decimal = Decimal
    #     self.test_decimal_roundtrip()
