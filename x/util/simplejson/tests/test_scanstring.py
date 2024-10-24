import sys
from unittest import TestCase

from ... import simplejson as json
from .. import decoder
from .compat import b


class TestScanString(TestCase):
    # The bytes type is intentionally not used in most of these tests
    # under Python 3 because the decoder immediately coerces to str before
    # calling scanstring. In Python 2 we are testing the code paths
    # for both unicode and str.
    #
    # The reason this is done is because Python 3 would require
    # entirely different code paths for parsing bytes and str.
    #
    def test_py_scanstring(self):
        self._test_scanstring(decoder.py_scanstring)

    def _test_scanstring(self, scanstring):
        if sys.maxunicode == 65535:
            self.assertEqual(
                scanstring('"z\U0001d120x"', 1, None, True),
                ('z\U0001d120x', 6),
            )
        else:
            self.assertEqual(
                scanstring('"z\U0001d120x"', 1, None, True),
                ('z\U0001d120x', 5),
            )

        self.assertEqual(scanstring('"\\u007b"', 1, None, True), ('{', 8))

        self.assertEqual(
            scanstring(
                '"A JSON payload should be an object or array, not a string."',
                1,
                None,
                True,
            ),
            ('A JSON payload should be an object or array, not a string.', 60),
        )

        self.assertEqual(
            scanstring('["Unclosed array"', 2, None, True),
            ('Unclosed array', 17),
        )

        self.assertEqual(
            scanstring('["extra comma",]', 2, None, True),
            ('extra comma', 14),
        )

        self.assertEqual(
            scanstring('["double extra comma",,]', 2, None, True),
            ('double extra comma', 21),
        )

        self.assertEqual(
            scanstring('["Comma after the close"],', 2, None, True),
            ('Comma after the close', 24),
        )

        self.assertEqual(
            scanstring('["Extra close"]]', 2, None, True),
            ('Extra close', 14),
        )

        self.assertEqual(
            scanstring('{"Extra comma": true,}', 2, None, True),
            ('Extra comma', 14),
        )

        self.assertEqual(
            scanstring(
                '{"Extra value after close": true} "misplaced quoted value"',
                2,
                None,
                True,
            ),
            ('Extra value after close', 26),
        )

        self.assertEqual(
            scanstring('{"Illegal expression": 1 + 2}', 2, None, True),
            ('Illegal expression', 21),
        )

        self.assertEqual(
            scanstring('{"Illegal invocation": alert()}', 2, None, True),
            ('Illegal invocation', 21),
        )

        self.assertEqual(
            scanstring('{"Numbers cannot have leading zeroes": 013}', 2, None, True),
            ('Numbers cannot have leading zeroes', 37),
        )

        self.assertEqual(
            scanstring('{"Numbers cannot be hex": 0x14}', 2, None, True),
            ('Numbers cannot be hex', 24),
        )

        self.assertEqual(
            scanstring(
                '[[[[[[[[[[[[[[[[[[[["Too deep"]]]]]]]]]]]]]]]]]]]]',
                21,
                None,
                True,
            ),
            ('Too deep', 30),
        )

        self.assertEqual(
            scanstring('{"Missing colon" null}', 2, None, True),
            ('Missing colon', 16),
        )

        self.assertEqual(
            scanstring('{"Double colon":: null}', 2, None, True),
            ('Double colon', 15),
        )

        self.assertEqual(
            scanstring('{"Comma instead of colon", null}', 2, None, True),
            ('Comma instead of colon', 25),
        )

        self.assertEqual(
            scanstring('["Colon instead of comma": false]', 2, None, True),
            ('Colon instead of comma', 25),
        )

        self.assertEqual(
            scanstring('["Bad value", truth]', 2, None, True),
            ('Bad value', 12),
        )

        for c in map(chr, range(0x1F)):
            self.assertEqual(scanstring(c + '"', 0, None, False), (c, 2))
            self.assertRaises(ValueError, scanstring, c + '"', 0, None, True)

        self.assertRaises(ValueError, scanstring, '', 0, None, True)
        self.assertRaises(ValueError, scanstring, 'a', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\u', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\u0', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\u01', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\u012', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\u0123', 0, None, True)
        if sys.maxunicode > 65535:
            self.assertRaises(ValueError, scanstring, '\\ud834\\u"', 0, None, True)
            self.assertRaises(ValueError, scanstring, '\\ud834\\x0123"', 0, None, True)

        self.assertRaises(json.JSONDecodeError, scanstring, '\\u-123"', 0, None, True)
        # SJ-PT-23-01: Invalid Handling of Broken Unicode Escape Sequences
        self.assertRaises(json.JSONDecodeError, scanstring, '\\u EDD"', 0, None, True)

    def test_issue3623(self):
        self.assertRaises(ValueError, json.decoder.scanstring, 'xxx', 1, 'xxx')
        self.assertRaises(
            UnicodeDecodeError,
            json.encoder.encode_basestring_ascii,
            b('xx\xff'),
        )

    def test_overflow(self):
        # Python 2.5 does not have maxsize, Python 3 does not have maxint
        maxsize = getattr(sys, 'maxsize', getattr(sys, 'maxint', None))
        assert maxsize is not None
        self.assertRaises(OverflowError, json.decoder.scanstring, 'xxx', maxsize + 1)

    def test_surrogates(self):
        scanstring = json.decoder.scanstring

        def assertScan(given, expect, test_utf8=True):
            givens = [given]
            for given in givens:
                (res, count) = scanstring(given, 1, None, True)
                self.assertEqual(len(given), count)
                self.assertEqual(res, expect)

        assertScan('"z\\ud834\\u0079x"', 'z\ud834yx')
        assertScan('"z\\ud834\\udd20x"', 'z\U0001d120x')
        assertScan('"z\\ud834\\ud834\\udd20x"', 'z\ud834\U0001d120x')
        assertScan('"z\\ud834x"', 'z\ud834x')
        assertScan('"z\\udd20x"', 'z\udd20x')
        assertScan('"z\ud834x"', 'z\ud834x')
        # It may look strange to join strings together, but Python is drunk.
        # https://gist.github.com/etrepum/5538443
        assertScan('"z\\ud834\udd20x12345"', ''.join(['z\ud834', '\udd20x12345']))
        assertScan('"z\ud834\\udd20x"', ''.join(['z\ud834', '\udd20x']))
        # these have different behavior given UTF8 input, because the surrogate
        # pair may be joined (in maxunicode > 65535 builds)
        assertScan(
            ''.join(['"z\ud834', '\udd20x"']),
            ''.join(['z\ud834', '\udd20x']),
            test_utf8=False,
        )

        self.assertRaises(ValueError, scanstring, '"z\\ud83x"', 1, None, True)
        self.assertRaises(ValueError, scanstring, '"z\\ud834\\udd2x"', 1, None, True)
