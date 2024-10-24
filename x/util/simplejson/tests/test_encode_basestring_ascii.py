from unittest import TestCase

from ... import simplejson as json
from .. import encoder
from .compat import b


CASES = [
    (
        "/\\\"\ucafe\ubabe\uab98\ufcde\ubcda\uef4a\x08\x0c\n\r\t`1~!@#$%^&*()_+-=[]{}|;:',./<>?",
        '"/\\\\\\"\\ucafe\\ubabe\\uab98\\ufcde\\ubcda\\uef4a\\b\\f\\n\\r\\t`1~!@#$%^&*()_+-=[]{}|;:\',./<>?"',
    ),
    (
        '\u0123\u4567\u89ab\ucdef\uabcd\uef4a',
        '"\\u0123\\u4567\\u89ab\\ucdef\\uabcd\\uef4a"',
    ),
    ('controls', '"controls"'),
    ('\x08\x0c\n\r\t', '"\\b\\f\\n\\r\\t"'),
    (
        '{"object with 1 member":["array with 1 element"]}',
        '"{\\"object with 1 member\\":[\\"array with 1 element\\"]}"',
    ),
    (' s p a c e d ', '" s p a c e d "'),
    ('\U0001d120', '"\\ud834\\udd20"'),
    ('\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    (b('\xce\xb1\xce\xa9'), '"\\u03b1\\u03a9"'),
    ('\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    (b('\xce\xb1\xce\xa9'), '"\\u03b1\\u03a9"'),
    ('\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    ('\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    ("`1~!@#$%^&*()_+-={':[,]}|;.</>?", '"`1~!@#$%^&*()_+-={\':[,]}|;.</>?"'),
    ('\x08\x0c\n\r\t', '"\\b\\f\\n\\r\\t"'),
    (
        '\u0123\u4567\u89ab\ucdef\uabcd\uef4a',
        '"\\u0123\\u4567\\u89ab\\ucdef\\uabcd\\uef4a"',
    ),
]


class TestEncodeBaseStringAscii(TestCase):
    def test_py_encode_basestring_ascii(self):
        self._test_encode_basestring_ascii(encoder.py_encode_basestring_ascii)

    def _test_encode_basestring_ascii(self, encode_basestring_ascii):
        fname = encode_basestring_ascii.__name__
        for input_string, expect in CASES:
            result = encode_basestring_ascii(input_string)
            # self.assertEqual(result, expect,
            #    '{0!r} != {1!r} for {2}({3!r})'.format(
            #        result, expect, fname, input_string))
            self.assertEqual(
                result,
                expect,
                '%r != %r for %s(%r)' % (result, expect, fname, input_string),
            )

    def test_sorted_dict(self):
        items = [('one', 1), ('two', 2), ('three', 3), ('four', 4), ('five', 5)]
        s = json.dumps(dict(items), sort_keys=True)
        self.assertEqual(s, '{"five": 5, "four": 4, "one": 1, "three": 3, "two": 2}')
