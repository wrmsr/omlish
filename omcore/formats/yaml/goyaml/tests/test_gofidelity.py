# @om-lite
"""
Regression tests pinning translation behaviors to the go-yaml originals.

Every expected value in here was captured by running the same input through go-yaml itself (at the revision named in
the package README), via yaml.Unmarshal into interface{}, parser.ParseBytes(...).String(), or lexer.Tokenize. If one
of these fails, the translation has drifted from go.
"""
import math
import unittest

from .. import tokens as tokens_mod
from ..ast import SequenceYamlNode
from ..ast import YamlAsts
from ..ast import yaml_parent
from ..decoding import ImmediateYamlBytesReader
from ..decoding import YamlCommentMap
from ..decoding import YamlCommentPosition
from ..decoding import YamlDecoder
from ..decoding import yaml_decode
from ..errors import EofYamlError
from ..errors import YamlError
from ..gostd import YamlGoStrconvRangeError
from ..gostd import YamlGoStrconvSyntaxError
from ..gostd import yaml_go_atoi
from ..gostd import yaml_go_b64_std_decode
from ..gostd import yaml_go_format_float
from ..gostd import yaml_go_parse_float
from ..gostd import yaml_go_parse_int
from ..gostd import yaml_go_parse_uint
from ..gostd import yaml_go_rune_str
from ..gostd import yaml_go_sprint
from ..gostd import yaml_go_trim_prefix
from ..gostd import yaml_go_trim_suffix
from ..parsing import yaml_parse_str
from ..scanning import yaml_tokenize
from ..tokens import YamlToken
from ..tokens import YamlTokenType


def _parse_file(s):
    f = yaml_parse_str(s)
    assert not isinstance(f, YamlError), f
    return f


def _parse_err(s):
    f = yaml_parse_str(s)
    assert isinstance(f, YamlError), f
    return f


class GostdTest(unittest.TestCase):
    def test_trim_prefix(self):
        # strings.TrimPrefix removes one exact prefix, not a character set
        self.assertEqual(yaml_go_trim_prefix('0x0', '0x'), '0')
        self.assertEqual(yaml_go_trim_prefix('--5', '-'), '-5')
        self.assertEqual(yaml_go_trim_prefix('  \tx', ' '), ' \tx')
        self.assertEqual(yaml_go_trim_prefix('abc', 'x'), 'abc')
        self.assertEqual(yaml_go_trim_prefix('abc', ''), 'abc')

    def test_trim_suffix(self):
        self.assertEqual(yaml_go_trim_suffix('x\n\n', '\n'), 'x\n')
        self.assertEqual(yaml_go_trim_suffix('3--', '-'), '3-')
        self.assertEqual(yaml_go_trim_suffix('abc', ''), 'abc')

    def test_parse_int(self):
        self.assertEqual(yaml_go_parse_int('-ff', 16), -255)
        self.assertEqual(yaml_go_parse_int('+5', 10), 5)
        self.assertIsInstance(yaml_go_parse_int(' 5', 10), YamlGoStrconvSyntaxError)
        self.assertIsInstance(yaml_go_parse_int('5_0', 10), YamlGoStrconvSyntaxError)
        # arabic-indic digits
        self.assertIsInstance(yaml_go_parse_int('\u0661\u0662\u0663', 10), YamlGoStrconvSyntaxError)
        self.assertIsInstance(yaml_go_parse_int('', 10), YamlGoStrconvSyntaxError)
        # range errors carry go's clamped value
        e = yaml_go_parse_int('99999999999999999999', 10)
        assert isinstance(e, YamlGoStrconvRangeError)
        self.assertEqual(e.value, (1 << 63) - 1)
        e = yaml_go_parse_int('-99999999999999999999', 10)
        assert isinstance(e, YamlGoStrconvRangeError)
        self.assertEqual(e.value, -(1 << 63))

    def test_parse_uint(self):
        self.assertEqual(yaml_go_parse_uint('0', 16), 0)
        self.assertEqual(yaml_go_parse_uint('18446744073709551615', 10), (1 << 64) - 1)
        self.assertIsInstance(yaml_go_parse_uint('+1', 10), YamlGoStrconvSyntaxError)
        self.assertIsInstance(yaml_go_parse_uint('-1', 10), YamlGoStrconvSyntaxError)
        self.assertIsInstance(yaml_go_parse_uint('18446744073709551616', 10), YamlGoStrconvRangeError)
        self.assertIsInstance(yaml_go_parse_uint('0x10', 16), YamlGoStrconvSyntaxError)  # no prefix with explicit base
        self.assertIsInstance(yaml_go_parse_uint('8', 8), YamlGoStrconvSyntaxError)

    def test_atoi(self):
        self.assertEqual(yaml_go_atoi('42'), 42)
        e = yaml_go_atoi('99999999999999999999')
        assert isinstance(e, YamlGoStrconvRangeError)
        self.assertEqual(e.value, 9223372036854775807)

    def test_parse_float(self):
        self.assertEqual(yaml_go_parse_float('1_000.5'), 1000.5)
        self.assertEqual(yaml_go_parse_float('1.5e1_0'), 1.5e10)
        self.assertIsInstance(yaml_go_parse_float('_1.5'), YamlGoStrconvSyntaxError)
        self.assertIsInstance(yaml_go_parse_float('1._5'), YamlGoStrconvSyntaxError)
        self.assertIsInstance(yaml_go_parse_float('1.5_'), YamlGoStrconvSyntaxError)
        self.assertIsInstance(yaml_go_parse_float(' 1.5'), YamlGoStrconvSyntaxError)
        self.assertEqual(yaml_go_parse_float('0x1p3'), 8.0)
        self.assertIsInstance(yaml_go_parse_float('0x1.8'), YamlGoStrconvSyntaxError)  # hex float requires a p exponent
        self.assertEqual(yaml_go_parse_float('Infinity'), math.inf)
        self.assertEqual(yaml_go_parse_float('-inf'), -math.inf)
        nan = yaml_go_parse_float('nan')
        assert isinstance(nan, float)
        self.assertTrue(math.isnan(nan))
        self.assertIsInstance(yaml_go_parse_float('+nan'), YamlGoStrconvSyntaxError)
        # overflow is a range error carrying the clamped infinity; underflow to zero is not an error
        e = yaml_go_parse_float('1e999')
        assert isinstance(e, YamlGoStrconvRangeError)
        self.assertEqual(e.value, math.inf)
        self.assertEqual(yaml_go_parse_float('1e-999'), 0.0)

    def test_format_float(self):
        # expected values captured from go fmt.Sprint(float64)
        for f, s in [
            (1.0, '1'),
            (1.5, '1.5'),
            (5.0, '5'),
            (-2.5, '-2.5'),
            (0.0, '0'),
            (100000.0, '100000'),
            (999999.5, '999999.5'),
            (1000000.0, '1e+06'),
            (1234567.8, '1.2345678e+06'),
            (123456789.123, '1.23456789123e+08'),
            (1e15, '1e+15'),
            (1e21, '1e+21'),
            (0.0001, '0.0001'),
            (0.00001, '1e-05'),
            (12345.6789, '12345.6789'),
            (3e300, '3e+300'),
            (1.0 / 3.0, '0.3333333333333333'),
            (math.inf, '+Inf'),
            (-math.inf, '-Inf'),
            (math.nan, 'NaN'),
        ]:
            self.assertEqual(yaml_go_format_float(f), s)

    def test_sprint(self):
        self.assertEqual(yaml_go_sprint(True), 'true')
        self.assertEqual(yaml_go_sprint(False), 'false')
        self.assertEqual(yaml_go_sprint(1.0), '1')
        self.assertEqual(yaml_go_sprint(42), '42')
        self.assertEqual(yaml_go_sprint('x'), 'x')
        self.assertEqual(yaml_go_sprint(None), '<nil>')

    def test_rune_str(self):
        self.assertEqual(yaml_go_rune_str(0x41), 'A')
        self.assertEqual(yaml_go_rune_str(0x1F601), '\U0001f601')
        self.assertEqual(yaml_go_rune_str(0xDC00), '�')  # lone surrogate
        self.assertEqual(yaml_go_rune_str(0x110000), '�')  # beyond unicode
        self.assertEqual(yaml_go_rune_str(0xFFFFFFFF), '�')  # int32 wrap to -1

    def test_b64_std_decode(self):
        # expected values captured from go base64.StdEncoding.DecodeString (which returns the partial decode on error)
        self.assertEqual(yaml_go_b64_std_decode('aGVsbG8='), b'hello')
        self.assertEqual(yaml_go_b64_std_decode('aGVs\nbG8='), b'hello')  # CR/LF ignored
        self.assertEqual(yaml_go_b64_std_decode('aGVs bG8='), b'hel')  # space is illegal
        self.assertEqual(yaml_go_b64_std_decode('aGVsbG8'), b'hel')  # truncated final quantum
        self.assertEqual(yaml_go_b64_std_decode('aGVsbG8=='), b'hello')  # trailing garbage after padding
        self.assertEqual(yaml_go_b64_std_decode('YQ==YQ=='), b'a')  # data after padded quantum
        self.assertEqual(yaml_go_b64_std_decode('!!!invalid!!!'), b'')


class TokensTest(unittest.TestCase):
    def test_number_prefixes(self):
        # go TrimPrefix removes '0x' etc. exactly once; all-zero literals must still parse
        self.assertEqual(yaml_decode('a: 0x0'), {'a': 0})
        self.assertEqual(yaml_decode('a: 0b0'), {'a': 0})
        self.assertEqual(yaml_decode('a: 0o0'), {'a': 0})
        self.assertEqual(yaml_decode('a: 0x00ff'), {'a': 255})
        # doubled signs are not numbers in go
        self.assertEqual(yaml_decode('a: --5'), {'a': '--5'})
        self.assertEqual(yaml_decode('a: ++1'), {'a': '++1'})

    def test_number_range(self):
        # values beyond uint64/int64 are String tokens in go (strconv range error)
        self.assertEqual(yaml_decode('a: 99999999999999999999'), {'a': '99999999999999999999'})
        self.assertEqual(yaml_decode('a: 1.0e999'), {'a': '1.0e999'})
        # but is_need_quoted still treats them as numbers (go's isNumber returns true on ErrRange)
        self.assertTrue(tokens_mod._yaml_is_need_quoted('99999999999999999999'))  # noqa

    def test_number_text(self):
        num = tokens_mod.yaml_to_number('0x01')
        assert num is not None
        self.assertEqual(num.text, '01')  # go: TrimPrefix leaves the leading zero

    def test_timestamps(self):
        # expected values captured from go time.Parse over the timestampFormats table
        for value, expected in [
            ('2001-12-15T02:59:43Z', True),  # fractional seconds are optional
            ('2001-12-15T02:59:43.1Z', True),
            ('2001-12-15T02:59:43.1234567890Z', True),  # any number of fractional digits
            ('2001-12-15T02:59:43,5Z', True),  # comma separator accepted by go
            ('2001-12-14t21:59:43.10-05:00', True),  # lower-case t, numeric offset
            ('2001-12-15T2:59:43Z', True),  # 1-2 digit hour
            ('2001-12-15T02:59:43.1z', False),  # lower-case zone z
            ('2001-12-15T02:59:43+25:00', False),  # offset hours <= 24
            ('2001-12-15T02:59:43+05:70', False),  # offset minutes <= 59
            ('2001-12-15T02:59:43', False),  # zone required by RFC3339 layouts
            ('2001-12-14 21:59:43', True),  # DateTime
            ('2001-12-15 2:59:43.10', True),  # fraction accepted even though the layout has none
            ('2001-12-14 21:59:43,10', True),
            ('2001-12-14 21:59:43.', False),  # separator requires digits
            ('2001-01-02 3:4:5', False),  # zero-padded minute/second fields need two digits
            ('2001-12-14', True),  # DateOnly
            ('2001-1-2', False),  # zero-padded month/day fields need two digits
            ('2001-02-29', False),  # day range is validated
            ('0000-01-01', True),  # go permits year zero
            ('03:04', True),  # "15:4" layout
            ('3:04', True),
            ('03:4', True),
            ('24:00', False),
            ('23:60', False),
        ]:
            self.assertEqual(tokens_mod._yaml_is_timestamp(value), expected, value)  # noqa


class ScanningTest(unittest.TestCase):
    def test_block_scalar_chomping(self):
        # clip mode keeps exactly one trailing newline (TrimSuffix removes one per iteration, not all)
        self.assertEqual(yaml_decode('a: |\n  x\n\nb: c\n'), {'a': 'x\n', 'b': 'c'})
        self.assertEqual(yaml_decode('a: |\n  x\n\n\nb: c\n'), {'a': 'x\n', 'b': 'c'})
        self.assertEqual(yaml_decode('a: |-\n  x\n\nb: c\n'), {'a': 'x', 'b': 'c'})
        self.assertEqual(yaml_decode('a: |+\n  x\n\nb: c\n'), {'a': 'x\n\n', 'b': 'c'})
        self.assertEqual(yaml_decode('a: >\n  x\n\nb: c\n'), {'a': 'x\n', 'b': 'c'})

    def test_invalid_token_in_stream(self):
        # go's Scan appends the invalid token to the returned stream so the parser can report it
        tks = yaml_tokenize('@')
        self.assertEqual(len(tks), 1)
        self.assertEqual(tks[0].type, YamlTokenType.INVALID)
        self.assertIsNotNone(tks.invalid_token())

    def test_scan_errors_reported(self):
        # all of these silently "succeeded" while invalid tokens were dropped
        _parse_err('@')
        _parse_err('a: "\\."\n')  # unknown escape character
        _parse_err('key: "missing closing quote\n')
        _parse_err("key: 'missing closing quote\n")
        _parse_err('---\na:\n\tb: c\n')  # tab indentation
        _parse_err('!invalid{}tag scalar\n')
        _parse_err('block: ># comment\n  scalar\n')
        _parse_err('a: |3--\n    foo\n')  # invalid header option
        _parse_err('a: | 2\n    foo\n')  # ParseInt rejects the leading space
        _parse_err('---\nblock scalar: |\n     \n  more spaces at the beginning\n  are invalid\n')

    def test_block_scalar_header_options(self):
        # go trims one leading '-'/'+' from the option, so |--3 parses as indent -3 (ignored)
        self.assertEqual(yaml_decode('a: |--3\n     foo\n'), {'a': 'foo'})

    def test_sequence_entry_at_eof(self):
        # 'nc != 0' is go's rune-zero check; a lone '-' at end of source is a sequence entry
        self.assertEqual(yaml_decode('-'), [None])
        tks = yaml_tokenize('-')
        self.assertEqual(tks[0].type, YamlTokenType.SEQUENCE_ENTRY)

    def test_tab_after_multiple_spaces(self):
        # go trims only one leading space before its tab checks, so two spaces + tab scans fine
        self.assertEqual(yaml_decode('  \ta: b\n'), {'a': 'b'})
        self.assertEqual(yaml_decode('  \t- a\n'), ['a'])

    def test_unicode_escapes(self):
        # go converts invalid runes to U+FFFD instead of erroring
        self.assertEqual(yaml_decode('a: "\\Uffffffff"'), {'a': '�'})
        self.assertEqual(yaml_decode('a: "\\udc00"'), {'a': '�'})
        self.assertEqual(yaml_decode('a: "\\U0001F601"'), {'a': '\U0001f601'})


class ParsingTest(unittest.TestCase):
    def test_document_header_kept(self):
        f = _parse_file('---\na: 1\n')
        self.assertIsNotNone(f.docs[0].start)
        self.assertEqual(f.docs[0].start.type, YamlTokenType.DOCUMENT_HEADER)
        self.assertEqual(f.string(), '---\na: 1\n')

    def test_document_header_second_doc(self):
        f = _parse_file('a: 1\n---\nb: 2\n')
        self.assertIsNone(f.docs[0].start)
        self.assertIsNotNone(f.docs[1].start)
        self.assertEqual(f.string(), 'a: 1\n---\nb: 2\n')

    def test_sequence_entry_tokens(self):
        # each entry must carry its own '-' token, not the first one's (go shadows seqTk per iteration)
        f = _parse_file('- a\n- b\n')
        seq = f.docs[0].body
        self.assertIsInstance(seq, SequenceYamlNode)
        self.assertEqual(seq.entries[0].start.position.line, 1)
        self.assertEqual(seq.entries[1].start.position.line, 2)

    def test_sequence_anchor_then_empty_entry(self):
        # the anchor on entry two must not swallow entry three
        self.assertEqual(yaml_decode('- x\n- &a\n-\n'), ['x', None, None])

    def test_flow_map_missing_value_errors(self):
        # truncated flow maps return syntax errors (go's nil-receiver Type() check), not crashes
        _parse_err('{a:')
        _parse_err('{a')
        _parse_err('{a: b,')


class AstTest(unittest.TestCase):
    def test_merge_key_marshal_yaml(self):
        tks = yaml_tokenize('<<: *a')
        mk = YamlAsts.merge_key(tks[0])
        self.assertEqual(mk.marshal_yaml(), '<<')

    def test_infinity_default_value(self):
        tks = yaml_tokenize('a: .inf')
        node = YamlAsts.infinity(tks[-1])
        self.assertEqual(node.value, math.inf)
        # go's switch has no default; unknown spellings keep the zero value
        tk = tks[-1]
        tk.value = '.INf'
        self.assertEqual(YamlAsts.infinity(tk).value, 0.0)

    def test_bool_invalid_value(self):
        # b, _ := strconv.ParseBool(...) - the error is discarded and false kept
        tks = yaml_tokenize('a: true')
        tk = tks[-1]
        tk.value = 'yes'
        self.assertIs(YamlAsts.bool_(tk).value, False)

    def test_parent_finder_identity(self):
        # go compares node pointers; a structurally equal clone under a different parent must not match
        def clone_tk(t):
            t2 = YamlToken.clone(t)
            assert t2 is not None
            return t2

        tk = yaml_tokenize('x')[0]
        a = YamlAsts.string(tk)
        b = YamlAsts.string(clone_tk(tk))
        inner = YamlAsts.sequence(clone_tk(tk), True)
        inner.values.append(b)
        outer = YamlAsts.sequence(clone_tk(tk), True)
        outer.values.extend([a, inner])
        self.assertEqual(a, b)  # structurally equal on purpose
        self.assertIs(yaml_parent(outer, b), inner)

    def test_literal_in_sequence_roundtrip(self):
        # block_style_string must trim one exact prefix from literal lines (go TrimPrefix), preserving indentation
        f = _parse_file('- |\n   x\n- foo\n')
        self.assertEqual(f.string(), '- |\n   x\n- foo\n')

    def test_multiline_string_roundtrip(self):
        f = _parse_file('a: |\n  x\n\nb: c\n')
        self.assertEqual(f.string(), 'a: |\n  x\n\nb: c\n')


class DecodingTest(unittest.TestCase):
    def test_anchor_at_document_root(self):
        # go decodes into dst before returning nil; the anchored value must not be discarded
        self.assertEqual(yaml_decode('&a\n- x\n- y\n'), ['x', 'y'])
        self.assertEqual(yaml_decode('&a hello\n'), 'hello')
        self.assertEqual(yaml_decode('&a {b: c}\n'), {'b': 'c'})

    def test_empty_documents(self):
        # nil-body documents flow through nodeToValue (which yields nil) instead of crashing
        self.assertIsNone(yaml_decode(''))
        self.assertIsNone(yaml_decode('---\n'))
        self.assertIsNone(yaml_decode('# only a comment\n'))
        self.assertIsNone(yaml_decode('...\n'))

    def test_zero_docs_signal_eof(self):
        # go falls through to io.EOF for zero-document files; yaml.Unmarshal maps that to nil
        d = YamlDecoder(ImmediateYamlBytesReader(b'...\n'))
        self.assertIsInstance(d.decode(), EofYamlError)

    def test_undefined_alias(self):
        # a missing anchor is a returned error (go's nil map lookup), not a KeyError
        d = YamlDecoder(ImmediateYamlBytesReader(b'<<: *undefined\n'))
        v = d.decode()
        self.assertIsInstance(v, YamlError)
        self.assertIn('cannot find anchor by alias name undefined', v.message)

    def test_sprint_map_keys(self):
        # go fmt.Sprint: bools lower-case, floats in shortest go form
        self.assertEqual(yaml_decode('true: 1'), {'true': 1})
        self.assertEqual(yaml_decode('1.0: x'), {'1': 'x'})
        self.assertEqual(yaml_decode('1.5: x'), {'1.5': 'x'})
        self.assertEqual(yaml_decode('1000000.5: x'), {'1.0000005e+06': 'x'})

    def test_str_tag(self):
        self.assertEqual(yaml_decode('a: !!str true'), {'a': 'true'})
        self.assertEqual(yaml_decode('a: !!str 1000000.0'), {'a': '1e+06'})

    def test_bool_tag(self):
        self.assertEqual(yaml_decode('a: !!bool 1.0'), {'a': True})  # Sprint(1.0) == "1"
        self.assertEqual(yaml_decode('a: !!bool yes'), {'a': True})

    def test_int_tag(self):
        self.assertEqual(yaml_decode('a: !!int 5.0'), {'a': 5})  # Atoi(Sprint(5.0)) == Atoi("5")
        # Atoi range errors keep strconv's clamped value
        self.assertEqual(yaml_decode('a: !!int 99999999999999999999'), {'a': 9223372036854775807})
        self.assertEqual(yaml_decode('a: !!int -99999999999999999999'), {'a': -9223372036854775808})

    def test_float_tag(self):
        # bool is not an int kind in go; it falls through to zero
        self.assertEqual(yaml_decode('a: !!float true'), {'a': 0})
        v = yaml_decode('a: !!float "abc"')
        self.assertEqual(v, {'a': 0.0})
        self.assertIsInstance(v['a'], float)
        # ParseFloat range errors keep the clamped infinity
        self.assertEqual(yaml_decode('a: !!float "1e999"'), {'a': math.inf})

    def test_binary_tag(self):
        self.assertEqual(yaml_decode('a: !!binary "aGVsbG8="'), {'a': b'hello'})
        # go returns the partial decode with the error discarded
        self.assertEqual(yaml_decode('a: !!binary "aGVs bG8="'), {'a': b'hel'})
        self.assertEqual(yaml_decode('a: !!binary "!!!invalid!!!"'), {'a': b''})

    def test_comment_map(self):
        d = YamlDecoder(ImmediateYamlBytesReader(b'a: 1 # hi\n'))
        d.to_comment_map = YamlCommentMap()
        self.assertEqual(d.decode(), {'a': 1})
        [(path, comments)] = list(d.to_comment_map.items())
        self.assertEqual(path, '$.a')
        self.assertEqual(comments[0].position, YamlCommentPosition.LINE)
        self.assertEqual(comments[0].texts, [' hi'])

    def test_decode_from_node_matches_decode(self):
        # both entry points must produce the value via decode_value (go's decodeValue), incl. for anchor roots
        v1 = yaml_decode('&a {b: c}\n')
        f = _parse_file('&a {b: c}\n')
        d = YamlDecoder(ImmediateYamlBytesReader(b'&a {b: c}\n'))
        v2 = d.decode_from_node(f.docs[0].body)
        self.assertEqual(v1, {'b': 'c'})
        self.assertEqual(v2, {'b': 'c'})

    def test_cast_to_float_bool(self):
        d = YamlDecoder(ImmediateYamlBytesReader(b''))
        self.assertEqual(d.cast_to_float(True), 0)
        self.assertEqual(d.cast_to_float(2), 2.0)
        self.assertEqual(d.cast_to_float('1.5'), 1.5)
        v = d.cast_to_float('abc')
        self.assertEqual(v, 0.0)
        self.assertIsInstance(v, float)

    def test_is_yaml_file(self):
        d = YamlDecoder(ImmediateYamlBytesReader(b''))
        self.assertTrue(d.is_yaml_file('x.yml'))
        self.assertTrue(d.is_yaml_file('a/b.yaml'))
        self.assertFalse(d.is_yaml_file('x.txt'))
        self.assertFalse(d.is_yaml_file('yml'))


class RoundTripTest(unittest.TestCase):
    """String round-trips whose expected outputs were captured from go parser.ParseBytes(...).String()."""

    def test_roundtrips(self):
        for src, expected in [
            ('a: 1\n', 'a: 1\n'),
            ('---\na: 1\n', '---\na: 1\n'),
            ('a: 1\n---\nb: 2\n', 'a: 1\n---\nb: 2\n'),
            ('- |\n   x\n- foo\n', '- |\n   x\n- foo\n'),
            ('a: |\n  x\n\nb: c\n', 'a: |\n  x\n\nb: c\n'),
            ('a: &anchor\nb: *anchor\n', 'a: &anchor\nb: *anchor\n'),
        ]:
            f = _parse_file(src)
            self.assertEqual(f.string(), expected, repr(src))


if __name__ == '__main__':
    unittest.main()
