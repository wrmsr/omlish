# @om-lite
"""
Tests ported from go-yaml's decode_test.go and yaml_test.go.

Only cases whose decode target is generic were ported: interface{}, map[string]interface{} (and compositions of
generic containers), map[interface{}]interface{}, []interface{}, yaml.MapSlice, or plain scalar targets whose expected
value is directly the decoded generic value. Cases depending on struct tags, custom unmarshalers, strict /
DisallowUnknownField modes, encoder round-trips, reference file/dir machinery, typed scalar conversions
(int/uint/float32/time/duration targets), or goroutines were skipped.
"""
import math
import typing as ta
import unittest

from ..decoding import ImmediateYamlBytesReader
from ..decoding import YamlCommentMap
from ..decoding import YamlDecoder
from ..decoding import YamlMapItem
from ..decoding import YamlMapSlice
from ..decoding import yaml_decode
from ..errors import EofYamlError
from ..errors import YamlError
from ..parsing import yaml_parse_str


def _decoder(src):
    return YamlDecoder(ImmediateYamlBytesReader(src.encode()))


def _assert_strict(tc, actual, expected, msg=None):
    # go decodes untyped scalars into concrete interface{} values (uint64/int64/float64/bool/string); mirror that by
    # requiring exact python types, not just == (which would conflate 1/1.0/True).
    if isinstance(expected, dict):
        tc.assertIsInstance(actual, dict, msg)
        tc.assertEqual(set(actual.keys()), set(expected.keys()), msg)
        for k in expected:
            _assert_strict(tc, actual[k], expected[k], msg)
    elif isinstance(expected, list):
        tc.assertIsInstance(actual, list, msg)
        tc.assertEqual(len(actual), len(expected), msg)
        for a, e in zip(actual, expected):
            _assert_strict(tc, a, e, msg)
    else:
        tc.assertIs(type(actual), type(expected), msg)
        tc.assertEqual(actual, expected, msg)


class DecoderTest(unittest.TestCase):
    """Generic-target subset of go TestDecoder."""

    CASES: ta.ClassVar = [
        ('v: true\n', {'v': True}),
        ('v: 10', {'v': 10}),
        ('v: 0b10', {'v': 2}),
        ('v: -0b101010', {'v': -42}),
        (
            'v: -0b1000000000000000000000000000000000000000000000000000000000000000',
            {'v': -9223372036854775808},
        ),
        ('v: 0xA', {'v': 10}),
        ('v: .1', {'v': 0.1}),
        ('v: -.1', {'v': -0.1}),
        ('v: 0.1\n', {'v': 0.1}),
        ('v: 6.8523e+5', {'v': 6.8523e+5}),
        ('v: 685.230_15e+03', {'v': 685.23015e+03}),
        ('v: 685_230.15', {'v': 685230.15}),
        ('v: 685230', {'v': 685230}),
        ('v: +685_230', {'v': 685230}),
        ('v: 02472256', {'v': 685230}),
        ('v: 0x_0A_74_AE', {'v': 685230}),
        ('v: 0b1010_0111_0100_1010_1110', {'v': 685230}),

        # Bools from spec
        ('v: True', {'v': True}),
        ('v: TRUE', {'v': True}),
        ('v: False', {'v': False}),
        ('v: FALSE', {'v': False}),
        ('v: y', {'v': 'y'}),  # y or yes or Yes is string
        ('v: NO', {'v': 'NO'}),  # no or No or NO is string
        ('v: on', {'v': 'on'}),  # on is string

        # Single Quoted values.
        ("'1': '2'", {'1': '2'}),
        ('\'1\': \'"2"\'', {'1': '"2"'}),
        ("'1': ''''", {'1': "'"}),
        ("'1': '''2'''", {'1': "'2'"}),
        ("'1': 'B''z'", {'1': "B'z"}),
        ('\'1\': \'\\\'', {'1': '\\'}),
        ('\'1\': \'\\\\\'', {'1': '\\\\'}),
        ('\'1\': \'\\"2\\"\'', {'1': '\\"2\\"'}),
        ('\'1\': \'\\\\"2\\\\"\'', {'1': '\\\\"2\\\\"'}),
        ("'1': '   1\n    2\n    3'", {'1': '   1 2 3'}),
        ("'1': '\n    2\n    3'", {'1': ' 2 3'}),

        # Double Quoted values.
        ('"1": "2"', {'1': '2'}),
        ('"1": "\\"2\\""', {'1': '"2"'}),
        ('"1": "\\""', {'1': '"'}),
        ('"1": "X\\"z"', {'1': 'X"z'}),
        ('"1": "\\\\"', {'1': '\\'}),
        ('"1": "\\\\\\\\"', {'1': '\\\\'}),
        ('"1": "\\\\\\"2\\\\\\""', {'1': '\\"2\\"'}),
        ('\'1\': "   1\n    2\n    3"', {'1': '   1 2 3'}),
        ('\'1\': "\n    2\n    3"', {'1': ' 2 3'}),
        ('"1": "a\\x2Fb"', {'1': 'a/b'}),
        ('"1": "a\\u002Fb"', {'1': 'a/b'}),
        ('"1": "a\\x2Fb\\u002Fc\\U0000002Fd"', {'1': 'a/b/c/d'}),
        ('\'1\': "2\\n3"', {'1': '2\n3'}),
        ('\'1\': "2\\r\\n3"', {'1': '2\r\n3'}),
        ('\'1\': "a\\\nb\\\nc"', {'1': 'abc'}),
        ('\'1\': "a\\\r\nb\\\r\nc"', {'1': 'abc'}),
        ('\'1\': "a\\\rb\\\rc"', {'1': 'abc'}),

        ('a: -b_c', {'a': '-b_c'}),
        ('a: +b_c', {'a': '+b_c'}),
        ('a: 50cent_of_dollar', {'a': '50cent_of_dollar'}),

        # Nulls
        ('v:', {'v': None}),
        ('v: ~', {'v': None}),
        ('v: null', {'v': None}),
        ('v: Null', {'v': None}),
        ('v: NULL', {'v': None}),

        ('v: .inf\n', {'v': math.inf}),
        ('v: .Inf\n', {'v': math.inf}),
        ('v: .INF\n', {'v': math.inf}),
        ('v: -.inf\n', {'v': -math.inf}),
        ('v: -.Inf\n', {'v': -math.inf}),
        ('v: -.INF\n', {'v': -math.inf}),

        # Explicit tags.
        ("v: !!float '1.1'", {'v': 1.1}),
        ('v: !!float 0', {'v': 0.0}),
        ('v: !!float -1', {'v': -1.0}),
        ("v: !!null ''", {'v': None}),
        ('\n!!merge <<: { a: 1, b: 2 }\nc: 3\n', {'a': 1, 'b': 2, 'c': 3}),

        # Flow sequence
        ('v: [A,B]', {'v': ['A', 'B']}),
        ('v: [A,1,C]', {'v': ['A', 1, 'C']}),
        ('v: [a: b, c: d]', {'v': [{'a': 'b'}, {'c': 'd'}]}),
        ('v: [{a: b}, {c: d, e: f}]', {'v': [{'a': 'b'}, {'c': 'd', 'e': 'f'}]}),

        # Block sequence
        ('v:\n - A\n - B', {'v': ['A', 'B']}),
        ('v:\n - A\n - 1\n - C', {'v': ['A', 1, 'C']}),

        # Map inside interface with no type hints.
        ('a: {b: c}', {'a': {'b': 'c'}}),

        ('123\n', 123),

        ('v:\n- A\n- 1\n- B:\n  - 2\n  - 3\n', {'v': ['A', 1, {'B': [2, 3]}]}),
        ('a:\n  b: c\n', {'a': {'b': 'c'}}),
        ('a: {b: c, d: e}\n', {'a': {'b': 'c', 'd': 'e'}}),
        ('a: 100.5\n', {'a': 100.5}),
        ('b: 2\na: 1\nd: 4\nc: 3\nsub:\n  e: 5\n', {'b': 2, 'a': 1, 'd': 4, 'c': 3, 'sub': {'e': 5}}),

        # Anchors and aliases.
        (
            'key1: &anchor\n  subkey: *anchor\nkey2: *anchor\n',
            {'key1': {'subkey': None}, 'key2': {'subkey': None}},
        ),

        ('{a: , b: c}', {'a': None, 'b': 'c'}),
        ('v: [1,[2,[3,[4,5],6],7],8]', {'v': [1, [2, [3, [4, 5], 6], 7], 8]}),
        (
            'v: {a: {b: {c: {d: e},f: g},h: i},j: k}',
            {'v': {'a': {'b': {'c': {'d': 'e'}, 'f': 'g'}, 'h': 'i'}, 'j': 'k'}},
        ),
        ('---\n- a:\n    b:\n- c: d\n', [{'a': {'b': None}}, {'c': 'd'}]),
        ('---\na:\n  b:\nc: d\n', {'a': {'b': None}, 'c': 'd'}),
        ('---\na:\nb:\nc:\n', {'a': None, 'b': None, 'c': None}),
        ('---\na: go test ./...\nb:\nc:\n', {'a': 'go test ./...', 'b': None, 'c': None}),
        (
            '---\na: |\n  hello\n  ...\n  world\nb:\nc:\n',
            {'a': 'hello\n...\nworld\n', 'b': None, 'c': None},
        ),

        # Multi bytes
        ('"\\ud83e\\udd23"', '\U0001f923'),
        ('"\\uD83D\\uDE00\\uD83D\\uDE01"', '\U0001f600\U0001f601'),
        ('"\\uD83D\\uDE00a\\uD83D\\uDE01"', '\U0001f600a\U0001f601'),

        ('42: 100', {'42': 100}),
    ]

    def test_decoder(self):
        for source, expected in self.CASES:
            with self.subTest(source=source):
                _assert_strict(self, yaml_decode(source), expected, repr(source))

    def test_nan(self):
        for source in ['v: .nan\n', 'v: .NaN\n', 'v: .NAN\n']:
            with self.subTest(source=source):
                v = yaml_decode(source)
                self.assertEqual(list(v.keys()), ['v'], repr(source))
                self.assertIsInstance(v['v'], float, repr(source))
                self.assertTrue(math.isnan(v['v']), repr(source))

    def test_eof(self):
        # go rows flagged eof: true - Decode returns io.EOF before touching the destination.
        for source in ['%YAML 1.2\n---\n', '---\n', '...', '']:
            with self.subTest(source=source):
                self.assertIsInstance(_decoder(source).decode(), EofYamlError)

    def test_map_slice(self):
        # go decodes "a: 1\nb: 2\nc: 3\n" into a yaml.MapSlice destination; the generic equivalent is ordered mode.
        d = _decoder('a: 1\nb: 2\nc: 3\n')
        d.use_ordered_map = True
        v = d.decode()
        self.assertEqual(v, YamlMapSlice([
            YamlMapItem('a', 1),
            YamlMapItem('b', 2),
            YamlMapItem('c', 3),
        ]))


class DecoderInvalidTest(unittest.TestCase):
    """go TestDecoder_Invalid."""

    def test_invalid(self):
        d = _decoder('*-0')
        v = d.decode()
        self.assertIsInstance(v, YamlError)
        self.assertEqual(v.message, "could not find alias '-0'")  # go quotes with %q


class DecodeWithMergeKeyTest(unittest.TestCase):
    """go TestDecodeWithMergeKey, "decode with interface{}" subtest (the struct subtests were skipped)."""

    YML = '\na: &a\n  b: 1\n  c: hello\nitems:\n- <<: *a\n- <<: *a\n  c: world\n'

    def test_decode_with_interface(self):
        v = yaml_decode(self.YML)
        items = v['items']
        self.assertEqual(len(items), 2)
        b0 = items[0]['b']
        self.assertIsInstance(b0, int)  # go asserts uint64
        self.assertEqual(b0, 1)
        c0 = items[0]['c']
        self.assertIsInstance(c0, str)
        self.assertEqual(c0, 'hello')
        b1 = items[1]['b']
        self.assertIsInstance(b1, int)  # go asserts uint64
        self.assertEqual(b1, 1)
        c1 = items[1]['c']
        self.assertIsInstance(c1, str)
        self.assertEqual(c1, 'world')


class DecoderInvalidCasesTest(unittest.TestCase):
    """go TestDecoder_InvalidCases (the FormatError checks are go-specific and were not ported)."""

    def test_invalid_cases(self):
        v = _decoder('---\na:\n- b\n  c: d\n').decode()
        self.assertIsInstance(v, YamlError)


class DecoderEmptySequenceItemTest(unittest.TestCase):
    """go TestDecoder_EmptySequenceItem."""

    def test_before_sibling_mapping_key(self):
        out = yaml_decode('args:\n- a\n-\ncommand:\n- python')
        self.assertEqual(out['args'], ['a', None])
        self.assertEqual(out['command'], ['python'])

    def test_indented_sequence(self):
        out = yaml_decode('parent:\n  items:\n    - a\n    -\n  other: val')
        parent = out['parent']
        self.assertEqual(parent['items'], ['a', None])
        self.assertEqual(parent['other'], 'val')

    def test_empty_item_with_indented_value_on_next_line(self):
        out = yaml_decode('items:\n-\n  key: val\n- b')
        items = out['items']
        self.assertEqual(len(items), 2)
        self.assertIsInstance(items[0], dict)
        self.assertEqual(items[0]['key'], 'val')


class DecoderAllowDuplicateMapKeyTest(unittest.TestCase):
    """go TestDecoder_AllowDuplicateMapKey (the struct subtest was skipped)."""

    def test_map(self):
        d = _decoder('\na: b\na: c\n')
        d.allow_duplicate_map_key = True
        v = d.decode()
        assert not isinstance(v, YamlError)


class DecodeLiteralTest(unittest.TestCase):
    """go TestDecode_Literal (the custom unmarshaler receives the literal text; generically it decodes directly)."""

    def test_literal(self):
        v = yaml_decode('---\nvalue: |\n  {\n     "key": "value"\n  }\n')
        self.assertIsNotNone(v['value'])
        self.assertNotEqual(v['value'], '')


class DecoderUseOrderedMapTest(unittest.TestCase):
    """go TestDecoder_UseOrderedMap (the marshal round-trip check is replaced by direct structure equality)."""

    def test_use_ordered_map(self):
        d = _decoder('\na: b\nc: d\ne:\n  f: g\n  h: i\nj: k\n')
        d.use_ordered_map = True
        v = d.decode()
        self.assertIsInstance(v, YamlMapSlice)
        # go asserts key order and content by marshalling back to the original source
        self.assertEqual(v, YamlMapSlice([
            YamlMapItem('a', 'b'),
            YamlMapItem('c', 'd'),
            YamlMapItem('e', YamlMapSlice([YamlMapItem('f', 'g'), YamlMapItem('h', 'i')])),
            YamlMapItem('j', 'k'),
        ]))


class DecoderStreamTest(unittest.TestCase):
    """go TestDecoder_Stream."""

    def test_stream(self):
        d = _decoder('\n---\na: b\nc: d\n---\ne: f\ng: h\n---\ni: j\nk: l\n')
        values = []
        while True:
            v = d.decode()
            if isinstance(v, EofYamlError):
                break
            assert not isinstance(v, YamlError)
            values.append(v)
        self.assertEqual(len(values), 3)
        self.assertEqual(values[0]['a'], 'b')
        self.assertEqual(values[1]['e'], 'f')
        self.assertEqual(values[2]['i'], 'j')


class DecoderDecodeFromNodeTest(unittest.TestCase):
    """go TestDecoder_DecodeFromNode (the "value is not pointer" subtest is go-specific and was skipped)."""

    def test_has_reference(self):
        src = '\nanchor: &map\n  text: hello\nmap: *map'
        f = yaml_parse_str(src)
        assert not isinstance(f, YamlError)
        d = YamlDecoder(ImmediateYamlBytesReader(b''))
        body = f.docs[0].body
        assert body is not None
        v = d.decode_from_node(body)
        assert not isinstance(v, YamlError)
        self.assertEqual(v['map'], {'text': 'hello'})

    def test_with_reference_option(self):
        d = YamlDecoder(ImmediateYamlBytesReader(b''))
        d.reference_readers.append(ImmediateYamlBytesReader(b'\nmap: &map\n  text: hello'))
        f = yaml_parse_str('map: *map')
        assert not isinstance(f, YamlError)
        body = f.docs[0].body
        assert body is not None
        v = d.decode_from_node(body)
        assert not isinstance(v, YamlError)
        self.assertEqual(v['map'], {'text': 'hello'})


class DecoderDecodeWithAnchorAnyValueTest(unittest.TestCase):
    """go TestDecoder_DecodeWithAnchorAnyValue (ported generically; go decodes into a struct)."""

    def test_decode_with_anchor_any_value(self):
        v = yaml_decode('\ndef:\n  myenv: &my_env\n    - VAR1=1\n    - VAR2=2\nconfig:\n  env: *my_env\n')
        self.assertEqual(v['config']['env'], ['VAR1=1', 'VAR2=2'])


class DecoderTabCharacterAtRightTest(unittest.TestCase):
    """go TestDecoder_TabCharacterAtRight."""

    def test_tab_character_at_right(self):
        v = yaml_decode('\n- a: [2 , 2] \t\t\t\n  b: [2 , 2] \t\t\t\n  c: [2 , 2]')
        self.assertEqual(len(v), 1)
        self.assertEqual(len(v[0]), 3)


class DecoderCanonicalTest(unittest.TestCase):
    """go TestDecoder_Canonical."""

    def test_canonical(self):
        v = yaml_decode(
            '\n!!map {\n'
            '  ? !!str "explicit":!!str "entry",\n'
            '  ? !!str "implicit" : !!str "entry",\n'
            '  ? !!null "" : !!null "",\n'
            '}\n',
        )
        self.assertIsInstance(v, dict)
        self.assertEqual(v['explicit'], 'entry')
        self.assertEqual(v['implicit'], 'entry')
        self.assertIsNone(v['null'])


class DecodeWithSameAnchorTest(unittest.TestCase):
    """go TestDecodeWithSameAnchor (go decodes into struct{A, B, C, D int}{1, 2, 3, 3})."""

    def test_decode_with_same_anchor(self):
        v = yaml_decode('\na: &a 1\nb: &a 2\nc: &a 3\nd: *a\n')
        self.assertEqual(v, {'a': 1, 'b': 2, 'c': 3, 'd': 3})


class UnmarshalMapSliceParallelTest(unittest.TestCase):
    """go TestUnmarshalMapSliceParallel, ported single-threaded (goroutine parallelism is not applicable)."""

    CONTENT = (
        '\nsteps:\n'
        '  req0:\n'
        '    desc: Get /users/1\n'
        '    req:\n'
        '      /users/1:\n'
        '        get: nil\n'
        '    test: |\n'
        '      current.res.status == 200\n'
        '  req1:\n'
        '    desc: Get /private\n'
        '    req:\n'
        '      /private:\n'
        '        get: nil\n'
        '    test: |\n'
        '      current.res.status == 403\n'
        '  req2:\n'
        '    desc: Get /users\n'
        '    req:\n'
        '      /users:\n'
        '        get: nil\n'
        '    test: |\n'
        '      current.res.status == 200\n'
    )

    def test_unmarshal_map_slice(self):
        for _ in range(10):
            d = _decoder(self.CONTENT)
            d.use_ordered_map = True
            v = d.decode()
            assert not isinstance(v, YamlError)
            steps = {item.key: item.value for item in v}['steps']
            for s in steps:
                # go asserts s.Value is map[string]interface{} because its MapSlice destination applies only at the
                # top level; python's use_ordered_map applies recursively, so a mapping here is a YamlMapSlice.
                self.assertIsInstance(s.value, YamlMapSlice)


class DecodeErrorTest(unittest.TestCase):
    """go TestDecodeError."""

    def test_duplicated_map_key_name_with_anchor_alias(self):
        v = _decoder('&0: *0\n*0:\n*0:').decode()
        self.assertIsInstance(v, YamlError)


class Issue617Test(unittest.TestCase):
    """go TestIssue617."""

    def test_issue_617(self):
        v = yaml_decode("\na: !Not [!Equals [!Ref foo, 'bar']]\n")
        self.assertEqual(v, {'a': [['foo', 'bar']]})


class SetNullValueTest(unittest.TestCase):
    """go TestSetNullValue, "set null" subtests (the typed-pointer subtests were skipped)."""

    def test_set_null(self):
        for name, src in [('empty document', ''), ('null value', 'null')]:
            with self.subTest(name=name):
                self.assertIsNone(yaml_decode(src))


class DecoderSiblingAnchorAliasTest(unittest.TestCase):
    """go TestDecoder_SiblingAnchorAlias."""

    def test_simple_sibling_alias(self):
        result = yaml_decode('\na: &a\n  b: &b value\n  ref: *b\n')
        a = result['a']
        self.assertIsInstance(a, dict)
        self.assertEqual(a['b'], 'value')
        self.assertEqual(a['ref'], 'value')

    def test_multiple_sibling_aliases(self):
        result = yaml_decode(
            '\nconfig: &config\n'
            '  db: &db postgres://localhost/mydb\n'
            '  cache: &cache redis://localhost:6379\n'
            '  app:\n'
            '    database_url: *db\n'
            '    cache_url: *cache\n',
        )
        app = result['config']['app']
        self.assertEqual(app['database_url'], 'postgres://localhost/mydb')
        self.assertEqual(app['cache_url'], 'redis://localhost:6379')

    def test_nested_map_sibling_alias(self):
        result = yaml_decode(
            '\nservice: &service\n'
            '  auth: &auth\n'
            '    required: true\n'
            '    type: jwt\n'
            '  endpoint:\n'
            '    security: *auth\n',
        )
        security = result['service']['endpoint']['security']
        self.assertIsInstance(security, dict)
        self.assertIs(security['required'], True)
        self.assertEqual(security['type'], 'jwt')

    def test_self_recursion_still_detected(self):
        result = yaml_decode('\na: &a\n  self: *a\n')
        self.assertIsNone(result['a']['self'])


class StreamDecodingWithCommentTest(unittest.TestCase):
    """go TestStreamDecodingWithComment (from yaml_test.go)."""

    def test_stream_decoding_with_comment(self):
        yml = (
            '\n# comment\n'
            '---\n'
            'a:\n'
            '  b:\n'
            '    c: # comment\n'
            '---\n'
            'foo: bar # comment\n'
            '---\n'
            '- a\n'
            '- b\n'
            '- c # comment\n'
        )
        cm = YamlCommentMap()
        d = _decoder(yml)
        d.to_comment_map = cm
        comment_paths_with_doc_index = []
        while True:
            v = d.decode()
            if isinstance(v, EofYamlError):
                break
            assert not isinstance(v, YamlError)
            comment_paths_with_doc_index.append(list(cm.keys()))
            cm.clear()
        self.assertEqual(comment_paths_with_doc_index, [
            ['$.a.b.c'],
            ['$.foo'],
            ['$[2]'],
        ])


class DecodeKeepAddressTest(unittest.TestCase):
    """go TestDecodeKeepAddress (from yaml_test.go); go compares %p pointers, python compares identity."""

    def test_decode_keep_address(self):
        v = yaml_decode('\na: &a [_]\nb: &b [*a,*a]\nc: &c [*b,*b]\nd: &d [*c,*c]\n')
        a = v['a']
        b = v['b']
        for vv in v['b']:
            self.assertIs(vv, a)
        for vv in v['c']:
            self.assertIs(vv, b)


if __name__ == '__main__':
    unittest.main()
