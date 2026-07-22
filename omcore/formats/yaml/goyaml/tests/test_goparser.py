# ruff: noqa: UP006
# @om-lite
"""
Port of go-yaml's parser/parser_test.go.

Every source and expected value in here was taken verbatim from the go test file (at the revision named in the package
README). The go tests format errors with a "[line:col] " prefix and an annotated source snippet; the translation only
carries the bare core message, so error assertions here compare against the core message and keep the go position and
snippet in nearby comments.
"""
import typing as ta
import unittest

from ..ast import MappingValueYamlNode
from ..ast import MappingYamlNode
from ..ast import SequenceYamlNode
from ..ast import YamlAstVisitor
from ..ast import YamlNodeType
from ..ast import yaml_ast_walk
from ..errors import YamlError
from ..parsing import YAML_PARSE_COMMENTS
from ..parsing import yaml_parse_str


def _comment_text(node):
    cg = node.get_comment()
    assert cg is not None
    tk = cg.get_token()
    assert tk is not None
    return tk.value


def _trim_prefix(s, prefix):
    # strings.TrimPrefix
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


# Cases whose faithful port fails against the translation; each maps a (test, key) pair to a description.
SUSPECTED_DIVERGENCES: ta.Dict[str, str] = {}


class _PrevNextClearVisitor(YamlAstVisitor):
    """go parser_test.go 'Visitor': clears token prev/next links for every visited node."""

    def visit(self, node):
        tk = node.get_token()
        tk.prev = None
        tk.next = None
        return self


class _PathCapturer(YamlAstVisitor):
    """go parser_test.go 'pathCapturer'."""

    def __init__(self):
        self.captured_num = 0
        self.ordered_paths = []
        self.ordered_types = []
        self.ordered_tokens = []

    def visit(self, node):
        self.captured_num += 1
        self.ordered_paths.append(node.get_path())
        self.ordered_types.append(node.type())
        self.ordered_tokens.append(node.get_token())
        return self


class ParserTest(unittest.TestCase):
    # go: TestParser
    def test_parser(self):
        sources = [
            '',
            'null\n',
            '0_',
            '{}\n',
            'v: hi\n',
            'v: "true"\n',
            'v: "false"\n',
            'v: true\n',
            'v: false\n',
            'v: 10\n',
            'v: -10\n',
            'v: 42\n',
            'v: 4294967296\n',
            'v: "10"\n',
            'v: 0.1\n',
            'v: 0.99\n',
            'v: -0.1\n',
            'v: .inf\n',
            'v: -.inf\n',
            'v: .nan\n',
            'v: null\n',
            'v: ""\n',
            'v:\n- A\n- B\n',
            "a: '-'\n",
            '123\n',
            'hello: world\n',
            'a: null\n',
            'v:\n- A\n- 1\n- B:\n  - 2\n  - 3\n',
            'a:\n  b: c\n',
            'a: {x: 1}\n',
            't2: 2018-01-09T10:40:47Z\nt4: 2098-01-09T10:40:47Z\n',
            'a: [1, 2]\n',
            'a: {b: c, d: e}\n',
            'a: 3s\n',
            'a: <foo>\n',
            'a: "1:1"\n',
            'a: 1.2.3.4\n',
            'a: "2015-02-24T18:19:39Z"\n',
            "a: 'b: c'\n",
            "a: 'Hello #comment'\n",
            'a: abc <<def>> ghi',
            'a: <<abcd',
            'a: <<:abcd',
            'a: <<  :abcd',
            'a: 100.5\n',
            'a: bogus\n',
            'a: "\\0"\n',
            'b: 2\na: 1\nd: 4\nc: 3\nsub:\n  e: 5\n',
            '       a       :          b        \n',
            'a: b # comment\nb: c\n',
            '---\na: b\n',
            'a: b\n...\n',
            '%YAML 1.2\n---\n',
            'a: !!binary gIGC\n',
            'a: !!binary |\n  ' + 'kJCQ' * 17 + 'kJ\n  CQ\n',
            'v: !!foo 1',
            'v:\n- A\n- |-\n  B\n  C\n',
            'v:\n- A\n- >-\n  B\n  C\n',
            'v: |-\n  0\n',
            'v: |-\n  0\nx: 0',
            '"a\\n1\\nb"',
            '{"a":"b"}',
            '!!map {\n'
            '  ? !!str "explicit":!!str "entry",\n'
            '  ? !!str "implicit" : !!str "entry",\n'
            '  ? !!null "" : !!null "",\n'
            '}',
            '"a": a\n"b": b',
            "'a': a\n'b': b",
            'a: \r\n  b: 1\r\n',
            'a_ok: \r  bc: 2\r',
            'a_mk: \n  bd: 3\n',
            'a: :a',
            '{a: , b: c}',
            'value: >\n',
            'value: >\n\n',
            'value: >\nother:',
            'value: >\n\nother:',
            'a:\n-',
            'a: {foo}',
            'a: {foo,bar}',
            '\n{\n  a: {\n    b: c\n  },\n  d: e\n}\n',
            '\n[\n  a: {\n    b: c\n  }]\n',
            '\n{\n  a: {\n    b: c\n  }}\n',
            '\n- !tag\n  a: b\n  c: d\n',
            '\na: !tag\n  b: c\n',
            '\na: !tag\n  b: c\n  d: e\n',
            '\na:\n  b: c\n     \n',
            '\nfoo: xxx\n---\nfoo: yyy\n---\nfoo: zzz\n',
            "\nv:\n  a\t: 'a'\n  bb\t: 'a'\n",
            "\nv:\n  a : 'x'\n  b\t: 'y'\n",
            "\nv:\n  a\t: 'x'\n  b\t: 'y'\n  c\t\t: 'z'\n",
            '{a: &a c, *a : b}',
        ]
        for idx, src in enumerate(sources):
            with self.subTest(idx=idx, src=src):
                f = yaml_parse_str(src, 0)
                assert not isinstance(f, YamlError), src
                f.string()  # ensure no panic


class ParseEmptyDocumentTest(unittest.TestCase):
    # go: TestParseEmptyDocument
    def test_empty_document(self):
        f = yaml_parse_str('', YAML_PARSE_COMMENTS)
        assert not isinstance(f, YamlError)
        self.assertEqual(f.string(), '\n')

    def test_empty_document_with_comment_parse_comment_off(self):
        f = yaml_parse_str('# comment', 0)
        assert not isinstance(f, YamlError)
        self.assertEqual(f.string(), '\n')

    def test_empty_document_with_comment_parse_comment_on(self):
        f = yaml_parse_str('# comment', YAML_PARSE_COMMENTS)
        assert not isinstance(f, YamlError)
        self.assertEqual(f.string(), '# comment\n')


class ParseComplicatedDocumentTest(unittest.TestCase):
    # go: TestParseComplicatedDocument
    def test_parse_complicated_document(self):
        tests = [
            (
                """
american:
  - Boston Red Sox
  - Detroit Tigers
  - New York Yankees
national:
  - New York Mets
  - Chicago Cubs
  - Atlanta Braves
""",
                """
american:
  - Boston Red Sox
  - Detroit Tigers
  - New York Yankees
national:
  - New York Mets
  - Chicago Cubs
  - Atlanta Braves
""",
            ),
            (
                """
a:
  b: c
  d: e
  f: g
h:
  i: j
  k:
    l: m
    n: o
  p: q
r: s
""",
                """
a:
  b: c
  d: e
  f: g
h:
  i: j
  k:
    l: m
    n: o
  p: q
r: s
""",
            ),
            (
                """
- a:
  - b
  - c
- d
""",
                """
- a:
  - b
  - c
- d
""",
            ),
            (
                """
- a
- b
- c
 - d
 - e
- f
""",
                """
- a
- b
- c - d - e
- f
""",
            ),
            (
                """
elem1:
  - elem2:
      {a: b, c: d}
""",
                """
elem1:
  - elem2:
      {a: b, c: d}
""",
            ),
            (
                """
elem1:
  - elem2:
      [a, b, c, d]
""",
                """
elem1:
  - elem2:
      [a, b, c, d]
""",
            ),
            (
                """
a: 0 - 1
""",
                """
a: 0 - 1
""",
            ),
            (
                """
- a:
   b: c
   d: e
- f:
  g: h
""",
                """
- a:
   b: c
   d: e
- f:
  g: h
""",
            ),
            (
                """
a:
 b
 c
d: e
""",
                """
a: b c
d: e
""",
            ),
            (
                """
a
b
c
""",
                """
a b c
""",
            ),
            (
                """
a:
 - b
 - c
""",
                """
a:
 - b
 - c
""",
            ),
            (
                """
-     a     :
      b: c
""",
                """
- a:
  b: c
""",
            ),
            (
                """
- a:
   b
   c
   d
  hoge: fuga
""",
                """
- a: b c d
  hoge: fuga
""",
            ),
            (
                """
- a # ' " # - : %
- b # " # - : % '
- c # # - : % ' "
- d # - : % ' " #
- e # : % ' " # -
- f # % ' : # - :
""",
                """
- a
- b
- c
- d
- e
- f
""",
            ),
            (
                """
# comment
a: # comment
# comment
 b: c # comment
 # comment
d: e # comment
# comment
""",
                """
a:
 b: c
d: e
""",
            ),
            (
                """
a: b#notcomment
""",
                """
a: b#notcomment
""",
            ),
            (
                """
anchored: &anchor foo
aliased: *anchor
""",
                """
anchored: &anchor foo
aliased: *anchor
""",
            ),
            (
                """
---
- &CENTER { x: 1, y: 2 }
- &LEFT { x: 0, y: 2 }
- &BIG { r: 10 }
- &SMALL { r: 1 }

# All the following maps are equal:

- # Explicit keys
  x: 1
  y: 2
  r: 10
  label: center/big

- # Merge one map
  << : *CENTER
  r: 10
  label: center/big

- # Merge multiple maps
  << : [ *CENTER, *BIG ]
  label: center/big

- # Override
  << : [ *BIG, *LEFT, *SMALL ]
  x: 1
  label: center/big
""",
                """
---
- &CENTER {x: 1, y: 2}
- &LEFT {x: 0, y: 2}
- &BIG {r: 10}
- &SMALL {r: 1}
- x: 1
  y: 2
  r: 10
  label: center/big
- <<: *CENTER
  r: 10
  label: center/big
- <<: [*CENTER, *BIG]
  label: center/big
- <<: [*BIG, *LEFT, *SMALL]
  x: 1
  label: center/big
""",
            ),
            (
                """
a:
- - b
- - c
  - d
""",
                """
a:
- - b
- - c
  - d
""",
            ),
            (
                """
a:
  b:
    c: d
  e:
    f: g
    h: i
j: k
""",
                """
a:
  b:
    c: d
  e:
    f: g
    h: i
j: k
""",
            ),
            (
                """
---
a: 1
b: 2
...
---
c: 3
d: 4
...
""",
                """
---
a: 1
b: 2
...
---
c: 3
d: 4
...
""",
            ),
            (
                """
a:
  b: |
    {
      [ 1, 2 ]
    }
  c: d
""",
                """
a:
  b: |
    {
      [ 1, 2 ]
    }
  c: d
""",
            ),
            (
                """
|
    hoge
    fuga
    piyo""",
                """
|
    hoge
    fuga
    piyo
""",
            ),
            (
                """
v: |
 a
 b
 c""",
                """
v: |
 a
 b
 c
""",
            ),
            (
                """
a: |
   bbbbbbb


   ccccccc
d: eeeeeeeeeeeeeeeee
""",
                """
a: |
   bbbbbbb


   ccccccc
d: eeeeeeeeeeeeeeeee
""",
            ),
            (
                # go source has trailing spaces after 'a: b'
                '\na: b    \n  c\n',
                """
a: b c
""",
            ),
            (
                # go source has trailing spaces after 'a:'
                '\na:    \n  b: c\n',
                """
a:
  b: c
""",
            ),
            (
                # go source has trailing spaces after 'a: b'
                '\na: b    \nc: d\n',
                """
a: b
c: d
""",
            ),
            (
                """
- ab - cd
- ef - gh
""",
                """
- ab - cd
- ef - gh
""",
            ),
            (
                """
- 0 - 1
 - 2 - 3
""",
                """
- 0 - 1 - 2 - 3
""",
            ),
            (
                """
a - b - c: value
""",
                """
a - b - c: value
""",
            ),
            (
                """
a:
-
  b: c
  d: e
-
  f: g
  h: i
""",
                """
a:
- b: c
  d: e
- f: g
  h: i
""",
            ),
            (
                """
a: |-
  value
b: c
""",
                """
a: |-
  value
b: c
""",
            ),
            (
                """
a:  |+
  value
b: c
""",
                """
a: |+
  value
b: c
""",
            ),
            (
                """
- key1: val
  key2:
    (
      foo
      +
      bar
    )
""",
                """
- key1: val
  key2: ( foo + bar )
""",
            ),
            (
                """
"a": b
'c': d
"e": "f"
g: "h"
i: 'j'
""",
                """
"a": b
'c': d
"e": "f"
g: "h"
i: 'j'
""",
            ),
            (
                """
a:
  - |2
        b
    c: d
""",
                """
a:
  - |2
        b
    c: d
""",
            ),
            (
                """
a:
 b: &anchor
 c: &anchor2
d: e
""",
                """
a:
 b: &anchor
 c: &anchor2
d: e
""",
            ),
        ]
        for idx, (source, expect) in enumerate(tests):
            with self.subTest(idx=idx, source=source):
                f = yaml_parse_str(source, 0)
                assert not isinstance(f, YamlError), source
                got = f.string()
                self.assertEqual(got, _trim_prefix(expect, '\n'))
                v = _PrevNextClearVisitor()
                for doc in f.docs:
                    assert doc.body is not None
                    yaml_ast_walk(v, doc.body)
                self.assertEqual('\n' + f.string(), expect)


class ParseWhitespaceTest(unittest.TestCase):
    # go: TestParseWhitespace
    def test_parse_whitespace(self):
        tests = [
            (
                """
a: b

c: d


e: f
g: h
""",
                """
a: b

c: d

e: f
g: h
""",
            ),
            (
                """
a:
  - b: c
    d: e

  - f: g
    h: i
""",
                """
a:
  - b: c
    d: e

  - f: g
    h: i
""",
            ),
            (
                # duplicated case in the go table, kept as-is
                """
a:
  - b: c
    d: e

  - f: g
    h: i
""",
                """
a:
  - b: c
    d: e

  - f: g
    h: i
""",
            ),
            (
                """
a:
- b: c
  d: e

- f: g
  h: i
""",
                """
a:
- b: c
  d: e

- f: g
  h: i
""",
            ),
            (
                """
a:
# comment 1
- b: c
  d: e

# comment 2
- f: g
  h: i
""",
                """
a:
# comment 1
- b: c
  d: e

# comment 2
- f: g
  h: i
""",
            ),
            (
                """
a:
  # comment 1
  - b: c
    # comment 2
    d: e

  # comment 3
  # comment 4
  - f: g
    h: i # comment 5
""",
                """
a:
  # comment 1
  - b: c
    # comment 2
    d: e

  # comment 3
  # comment 4
  - f: g
    h: i # comment 5
""",
            ),
            (
                """
a:
  # comment 1
  - b: c
    # comment 2
    d: e

  # comment 3
  # comment 4
  - f: |
      g
      g
    h: i # comment 5
""",
                """
a:
  # comment 1
  - b: c
    # comment 2
    d: e

  # comment 3
  # comment 4
  - f: |
      g
      g
    h: i # comment 5
""",
            ),
            (
                """
a:
  # comment 1
  - b: c
    # comment 2
    d: e

  # comment 3
  # comment 4
  - f: |
      asd
      def

    h: i # comment 5
""",
                """
a:
  # comment 1
  - b: c
    # comment 2
    d: e

  # comment 3
  # comment 4
  - f: |
      asd
      def

    h: i # comment 5
""",
            ),
            (
                """
- b: c
  d: e

- f: g
  h: i # comment 4
""",
                """
- b: c
  d: e

- f: g
  h: i # comment 4
""",
            ),
            (
                """
a: null
b: null

d: e
""",
                """
a: null
b: null

d: e
""",
            ),
            (
                """
foo:
  bar: null # comment

  baz: 1
""",
                """
foo:
  bar: null # comment

  baz: 1
""",
            ),
            (
                """
foo:
  bar: null # comment

baz: 1
""",
                """
foo:
  bar: null # comment

baz: 1
""",
            ),
            (
                # go source indents this flow map with tab characters
                '\n'
                '{\n'
                '\t"apiVersion": "apps/v1",\n'
                '\t"kind": "Deployment",\n'
                '\t"metadata": {\n'
                '\t\t"name": "foo",\n'
                '\t\t"labels": {\n'
                '\t\t\t"app": "bar"\n'
                '\t\t}\n'
                '\t},\n'
                '\t"spec": {\n'
                '\t\t"replicas": 3,\n'
                '\t\t"selector": {\n'
                '\t\t\t"matchLabels": {\n'
                '\t\t\t\t"app": "bar"\n'
                '\t\t\t}\n'
                '\t\t},\n'
                '\t\t"template": {\n'
                '\t\t\t"metadata": {\n'
                '\t\t\t\t"labels": {\n'
                '\t\t\t\t\t"app": "bar"\n'
                '\t\t\t\t}\n'
                '\t\t\t}\n'
                '\t\t}\n'
                '\t}\n'
                '}\n',
                '\n'
                '{"apiVersion": "apps/v1", "kind": "Deployment", '
                '"metadata": {"name": "foo", "labels": {"app": "bar"}}, '
                '"spec": {"replicas": 3, "selector": {"matchLabels": {"app": "bar"}}, '
                '"template": {"metadata": {"labels": {"app": "bar"}}}}}\n',
            ),
        ]
        for idx, (source, expect) in enumerate(tests):
            with self.subTest(idx=idx, source=source):
                f = yaml_parse_str(source, YAML_PARSE_COMMENTS)
                assert not isinstance(f, YamlError), source
                self.assertEqual(f.string(), _trim_prefix(expect, '\n'))


class NewLineCharTest(unittest.TestCase):
    # go: TestNewLineChar - reads parser/testdata/{lf,cr,crlf}.yml; the file contents are inlined here.
    def test_new_line_char(self):
        for name, src in [
            ('lf.yml', 'a: "a"\n\nb: 1\n'),
            ('cr.yml', 'a: "a"\r\rb: 1\r'),
            ('crlf.yml', 'a: "a"\r\n\r\nb: 1\r\n'),
        ]:
            with self.subTest(name=name):
                f = yaml_parse_str(src, 0)
                assert not isinstance(f, YamlError), name
                expect = 'a: "a"\n\nb: 1\n'
                self.assertEqual(f.string(), expect)


class SyntaxErrorTest(unittest.TestCase):
    # go: TestSyntaxError. The expected values in go are full formatted messages with a "[line:col] " prefix and an
    # annotated snippet; the translation keeps only the core message. The go position (and, where the message embeds
    # %q-quoted text, the original quoting) is preserved in comments.
    def test_syntax_error(self):
        tests = [
            # go: [3:3] unexpected key name
            #    2 | a:
            # >  3 | - b
            #    4 |   c: d
            #          ^
            #    5 |   e: f
            #    6 |   g: h
            (
                '\na:\n- b\n  c: d\n  e: f\n  g: h',
                'unexpected key name',
            ),
            # go: [2:1] unexpected key name
            # >  2 | a
            #    3 | - b: c
            #        ^
            (
                '\na\n- b: c',
                'unexpected key name',
            ),
            # go: [1:1] unexpected directive value. document not started
            # >  1 | %YAML 1.1 {}
            #        ^
            (
                '%YAML 1.1 {}',
                'unexpected directive value. document not started',
            ),
            # go: [1:2] could not find flow map content
            # >  1 | {invalid
            #         ^
            (
                '{invalid',
                'could not find flow map content',
            ),
            # go: [1:1] could not find flow mapping end token '}'
            # >  1 | { "key": "value"
            #        ^
            (
                '{ "key": "value" ',
                "could not find flow mapping end token '}'",
            ),
            # go: [2:4] invalid header option: "invalidopt"
            # >  2 | a: |invalidopt
            #           ^
            #    3 |   foo
            (
                '\na: |invalidopt\n  foo\n',
                "invalid header option: 'invalidopt'",  # go quotes with %q
            ),
            # go: [3:1] non-map value is specified
            #    2 | a: 1
            # >  3 | b
            #        ^
            (
                '\na: 1\nb\n',
                'non-map value is specified',
            ),
            # go: [3:3] value is not allowed in this context. map key-value is pre-defined
            #    2 | a: 'b'
            # >  3 |   c: d
            #          ^
            (
                "\na: 'b'\n  c: d\n",
                'value is not allowed in this context. map key-value is pre-defined',
            ),
            # go: [3:3] value is not allowed in this context. map key-value is pre-defined
            #    2 | a: 'b'
            # >  3 |   - c
            #          ^
            (
                "\na: 'b'\n  - c\n",
                'value is not allowed in this context. map key-value is pre-defined',
            ),
            # go: [4:3] value is not allowed in this context. map key-value is pre-defined
            #    2 | a: 'b'
            #    3 |   # comment
            # >  4 |   - c
            #          ^
            (
                "\na: 'b'\n  # comment\n  - c\n",
                'value is not allowed in this context. map key-value is pre-defined',
            ),
            # go: [3:1] non-map value is specified
            #    2 | a: 1
            # >  3 | b
            #        ^
            #    4 | - c
            (
                '\na: 1\nb\n- c\n',
                'non-map value is specified',
            ),
            # go: [1:4] sequence end token ']' not found
            # >  1 | a: [
            #           ^
            (
                'a: [',
                "sequence end token ']' not found",
            ),
            # go: [1:4] could not find '[' character corresponding to ']'
            # >  1 | a: ]
            #           ^
            (
                'a: ]',
                "could not find '[' character corresponding to ']'",
            ),
            # go: [1:10] ',' or ']' must be specified
            # >  1 | a: [ [1] [2] [3] ]
            #                 ^
            (
                'a: [ [1] [2] [3] ]',
                "',' or ']' must be specified",
            ),
            # go: [2:4] block sequence entries are not allowed in this context
            # >  2 | a: -
            #           ^
            #    3 | b: -
            (
                '\na: -\nb: -\n',
                'block sequence entries are not allowed in this context',
            ),
            # go: [2:4] block sequence entries are not allowed in this context
            # >  2 | a: - 1
            #           ^
            #    3 | b: - 2
            (
                '\na: - 1\nb: - 2\n',
                'block sequence entries are not allowed in this context',
            ),
            # go: [1:4] could not find end character of single-quoted text
            # >  1 | a: 'foobarbaz
            #           ^
            (
                "a: 'foobarbaz",
                'could not find end character of single-quoted text',
            ),
            # go: [1:4] could not find end character of double-quoted text
            # >  1 | a: "\"key\": \"value:\"
            #           ^
            (
                'a: "\\"key\\": \\"value:\\"',
                'could not find end character of double-quoted text',
            ),
            # go: [1:8] ',' or ']' must be specified
            # >  1 | foo: [${should not be allowed}]
            #               ^
            (
                'foo: [${should not be allowed}]',
                "',' or ']' must be specified",
            ),
            # go: [1:8] ',' or ']' must be specified
            # >  1 | foo: [$[should not be allowed]]
            #               ^
            (
                'foo: [$[should not be allowed]]',
                "',' or ']' must be specified",
            ),
            # go: [2:1] could not find multi-line content
            #    1 | >
            # >  2 | >
            #        ^
            (
                '>\n>',
                'could not find multi-line content',
            ),
            # go: [2:1] could not find multi-line content
            #    1 | >
            # >  2 | 1
            #        ^
            (
                '>\n1',
                'could not find multi-line content',
            ),
            # go: [2:1] could not find multi-line content
            #    1 | |
            # >  2 | 1
            #        ^
            (
                '|\n1',
                'could not find multi-line content',
            ),
            # go: [2:3] invalid number of indent is specified in the multi-line header
            #    1 | a: >3
            # >  2 |   1
            #          ^
            (
                'a: >3\n  1',
                'invalid number of indent is specified in the multi-line header',
            ),
            # go: [5:5] value is not allowed in this context
            #    2 | a:
            #    3 |   - |
            #    4 |         b
            # >  5 |     c: d
            #            ^
            (
                '\na:\n  - |\n        b\n    c: d\n',
                'value is not allowed in this context',
            ),
            # go: [5:5] value is not allowed in this context
            #    2 | a:
            #    3 |   - |
            #    4 |         b
            # >  5 |     c:
            #            ^
            #    6 |       d: e
            (
                '\na:\n  - |\n        b\n    c:\n      d: e\n',
                'value is not allowed in this context',
            ),
            # go: [1:7] '@' is a reserved character
            # >  1 | key: [@val]
            #              ^
            (
                'key: [@val]',
                "'@' is a reserved character",
            ),
            # go: [1:7] '`' is a reserved character
            # >  1 | key: [`val]
            #              ^
            (
                'key: [`val]',
                "'`' is a reserved character",
            ),
            # go: [1:7] found an invalid key for this map
            # >  1 | {a: b}: v
            #              ^
            (
                '{a: b}: v',
                'found an invalid key for this map',
            ),
            # go: [1:4] found an invalid key for this map
            # >  1 | [a]: v
            #           ^
            (
                '[a]: v',
                'found an invalid key for this map',
            ),
            # go: [7:1] mapping key "foo" already defined at [2:1]
            #    4 |     foo: 2
            #    5 |   baz:
            #    6 |     foo: 3
            # >  7 | foo: 2
            #        ^
            (
                '\nfoo:\n  bar:\n    foo: 2\n  baz:\n    foo: 3\nfoo: 2\n',
                "mapping key 'foo' already defined at [2:1]",  # go quotes with %q
            ),
            # go: [7:5] mapping key "foo" already defined at [6:5]
            #    4 |     foo: 2
            #    5 |   baz:
            #    6 |     foo: 3
            # >  7 |     foo: 4
            #            ^
            (
                '\nfoo:\n  bar:\n    foo: 2\n  baz:\n    foo: 3\n    foo: 4\n',
                "mapping key 'foo' already defined at [6:5]",  # go quotes with %q
            ),
            # go: [1:13] could not find flow map content
            # >  1 | {"000":0000A,
            #                    ^
            (
                '{"000":0000A,',
                'could not find flow map content',
            ),
        ]
        for idx, (source, core) in enumerate(tests):
            with self.subTest(idx=idx, source=source):
                f = yaml_parse_str(source, 0)
                assert isinstance(f, YamlError), source
                self.assertEqual(f.message, core)


class CommentTest(unittest.TestCase):
    # go: TestComment
    def test_comment(self):
        tests = [
            (
                'map with comment',
                """
# commentA
a: #commentB
  # commentC
  b: c # commentD
  # commentE
  d: e # commentF
  # commentG
  f: g # commentH
# commentI
f: g # commentJ
# commentK
""",
                None,
            ),
            (
                'sequence with comment',
                """
# commentA
- a # commentB
# commentC
- b: # commentD
  # commentE
  - d # commentF
  - e # commentG
# commentH
""",
                None,
            ),
            (
                'anchor and alias',
                """
a: &x b # commentA
c: *x # commentB
""",
                None,
            ),
            (
                'multiline',
                """
# foo comment
# foo comment2
foo: # map key comment
  # bar above comment
  # bar above comment2
  bar: 10 # comment for bar
  # baz above comment
  # baz above comment2
  baz: bbbb # comment for baz
  piyo: # sequence key comment
  # sequence1 above comment 1
  # sequence1 above comment 2
  - sequence1 # sequence1
  # sequence2 above comment 1
  # sequence2 above comment 2
  - sequence2 # sequence2
  # sequence3 above comment 1
  # sequence3 above comment 2
  - false # sequence3
# foo2 comment
# foo2 comment2
foo2: &anchor text # anchor comment
# foo3 comment
# foo3 comment2
foo3: *anchor # alias comment
""",
                None,
            ),
            (
                'flow map with inline key comment',
                """
elem1:
  - elem2: # comment
      {a: b, c: d}
""",
                """
elem1:
  - elem2: # comment
      {a: b, c: d}
""",
            ),
            (
                'flow sequence with inline key comment',
                """
elem1:
  - elem2: # comment
      [a, b, c, d]
""",
                """
elem1:
  - elem2: # comment
      [a, b, c, d]
""",
            ),
            (
                'flow map with inline value comment',
                """
a:
  b: {} # comment
c: d
""",
                None,
            ),
            (
                'flow array with inline value comment',
                """
a:
  b: [] # comment
c: d
""",
                None,
            ),
            (
                'literal',
                """
foo: | # comment
  x: 42
""",
                None,
            ),
            (
                'folded',
                """
foo: > # comment
  x: 42
""",
                None,
            ),
            (
                'unattached comment',
                """
# This comment is in its own document
---
a: b
""",
                None,
            ),
            (
                'map with misaligned indentation in comments',
                """
 # commentA
a:  #commentB
   # commentC
  b: c  # commentD
    # commentE
  d: e  # commentF
 # commentG
""",
                """
# commentA
a: #commentB
  # commentC
  b: c # commentD
  # commentE
  d: e # commentF
# commentG
""",
            ),
            (
                'sequence with misaligned indentation in comments',
                """
 # commentA
- a  # commentB
 # commentC
- b:   # commentD
   # commentE
  - d  # commentF
    # commentG
  - e  # commentG
 # commentH
""",
                """
# commentA
- a # commentB
# commentC
- b: # commentD
  # commentE
  - d # commentF
  # commentG
  - e # commentG
# commentH
""",
            ),
        ]
        for name, yml, expected in tests:
            with self.subTest(name=name):
                f = yaml_parse_str(yml, YAML_PARSE_COMMENTS)
                assert not isinstance(f, YamlError), name
                got = '\n' + f.string()
                if expected is None:
                    expected = yml
                self.assertEqual(got, expected)


class CommentWithNullTest(unittest.TestCase):
    # go: TestCommentWithNull
    def test_same_line(self):
        content = """
foo:
  bar: # comment
  baz: 1
"""
        expected = """
foo:
  bar: # comment
  baz: 1"""
        f = yaml_parse_str(content, YAML_PARSE_COMMENTS)
        assert not isinstance(f, YamlError)
        self.assertEqual(len(f.docs), 1)
        got = f.docs[0].string()
        self.assertEqual(got, _trim_prefix(expected, '\n'))

    def test_next_line(self):
        content = """
foo:
  bar:
    # comment
  baz: 1
"""
        expected = """
foo:
  bar:
  # comment
  baz: 1"""
        f = yaml_parse_str(content, YAML_PARSE_COMMENTS)
        assert not isinstance(f, YamlError)
        self.assertEqual(len(f.docs), 1)
        got = f.docs[0].string()
        self.assertEqual(got, _trim_prefix(expected, '\n'))

    def test_next_line_and_different_indent(self):
        content = """
foo:
  bar:
 # comment
baz: 1"""
        f = yaml_parse_str(content, YAML_PARSE_COMMENTS)
        assert not isinstance(f, YamlError)
        self.assertEqual(len(f.docs), 1)
        expected = """
foo:
  bar:
# comment
baz: 1"""
        got = f.docs[0].string()
        self.assertEqual(got, _trim_prefix(expected, '\n'))


class SequenceCommentTest(unittest.TestCase):
    # go: TestSequenceComment. The go test's "foo[0].bar" / "baz[0]" subtests use the yaml path package
    # (yaml.PathString / path.FilterFile), which is untranslated, so only the string round-trip is ported.
    def test_sequence_comment(self):
        content = """
foo:
  - # comment
    bar: 1
baz:
  - xxx
"""
        f = yaml_parse_str(content, YAML_PARSE_COMMENTS)
        assert not isinstance(f, YamlError)
        self.assertEqual(len(f.docs), 1)
        expected = """
foo:
  # comment
  - bar: 1
baz:
  - xxx"""
        got = f.docs[0].string()
        self.assertEqual(got, _trim_prefix(expected, '\n'))


class CommentWithMapTest(unittest.TestCase):
    # go: TestCommentWithMap
    def test_comment_with_map(self):
        yml = """
single:
  # foo comment
  foo: bar

multiple:
    # a comment
    a: b
    # c comment
    c: d
"""
        f = yaml_parse_str(yml, YAML_PARSE_COMMENTS)
        assert not isinstance(f, YamlError)
        self.assertNotEqual(len(f.docs), 0)
        self.assertIsNotNone(f.docs[0].body)
        map_node = f.docs[0].body
        assert isinstance(map_node, MappingYamlNode)
        self.assertEqual(len(map_node.values), 2)

        single_node = map_node.values[0].value
        assert isinstance(single_node, MappingYamlNode)
        self.assertEqual(len(single_node.values), 1)
        self.assertEqual(_comment_text(single_node.values[0]), ' foo comment')

        multi_node = map_node.values[1].value
        assert isinstance(multi_node, MappingYamlNode)
        self.assertIsNone(multi_node.get_comment())
        self.assertEqual(len(multi_node.values), 2)
        self.assertEqual(_comment_text(multi_node.values[0]), ' a comment')
        self.assertEqual(_comment_text(multi_node.values[1]), ' c comment')


class InFlowStyleTest(unittest.TestCase):
    # go: TestInFlowStyle
    def test_in_flow_style(self):
        tests = [
            (
                """
  - foo
  - bar
  - baz
""",
                '[foo, bar, baz]\n',
            ),
            (
                """
foo: bar
baz: fizz
""",
                '{foo: bar, baz: fizz}\n',
            ),
            (
                """
foo:
  - bar
  - baz
  - fizz: buzz
""",
                '{foo: [bar, baz, {fizz: buzz}]}\n',
            ),
        ]
        for idx, (source, expect) in enumerate(tests):
            with self.subTest(idx=idx, source=source):
                f = yaml_parse_str(source, YAML_PARSE_COMMENTS)
                assert not isinstance(f, YamlError), source
                self.assertEqual(len(f.docs), 1)
                body = f.docs[0].body
                # go type-switches on the concrete node kinds that carry SetIsFlowStyle.
                assert isinstance(body, (MappingYamlNode, MappingValueYamlNode, SequenceYamlNode)), body
                body.set_is_flow_style(True)
                self.assertEqual(f.string(), expect)


class NodePathTest(unittest.TestCase):
    # go: TestNodePath
    def test_node_path(self):
        yml = """
a: # commentA
  b: # commentB
    c: foo # commentC
    d: bar # commentD
    e: baz # commentE
  f: # commentF
    g: hoge # commentG
  h: # commentH
   - list1 # comment list1
   - list2 # comment list2
   - list3 # comment list3
  i: fuga # commentI
j: piyo # commentJ
k.l.m.n: moge # commentKLMN
o#p: hogera # commentOP
q#.r: hogehoge # commentQR
"""
        f = yaml_parse_str(yml, YAML_PARSE_COMMENTS)
        assert not isinstance(f, YamlError)
        capturer = _PathCapturer()
        for doc in f.docs:
            assert doc.body is not None
            yaml_ast_walk(capturer, doc.body)
        comment_paths = []
        for i in range(capturer.captured_num):
            if capturer.ordered_types[i] == YamlNodeType.COMMENT:
                comment_paths.append(capturer.ordered_paths[i])
        expected_paths = [
            '$.a',
            '$.a.b',
            '$.a.b.c',
            '$.a.b.d',
            '$.a.b.e',
            '$.a.f',
            '$.a.f.g',
            '$.a.h',
            '$.a.h[0]',
            '$.a.h[1]',
            '$.a.h[2]',
            '$.a.i',
            '$.j',
            "$.'k.l.m.n'",
            '$.o#p',
            "$.'q#.r'",
        ]
        self.assertEqual(expected_paths, comment_paths)


if __name__ == '__main__':
    unittest.main()
