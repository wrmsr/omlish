# ruff: noqa: UP006
# @om-lite
"""
Port of go-yaml's lexer/lexer_test.go (TestTokenize, TestSingleLineToken_ValueLineColumnPosition,
TestMultiLineToken_ValueLineColumnPosition, TestInvalid, TestTokenOffset).

Every expected value in here comes verbatim from the go test source, with go string literals translated to python
(backtick strings are raw, double-quoted strings are interpreted).
"""
import typing as ta
import unittest

from ..scanning import yaml_tokenize
from ..tokens import YamlCharType
from ..tokens import YamlIndicator
from ..tokens import YamlTokenType


# In lexer_test.go every expected token's CharacterType/Indicator pair is fully determined by its Type; the compact
# (type, value, origin) case tuples below rely on this table to restore the two dropped fields.
_KINDS = {
    YamlTokenType.NULL: (YamlCharType.MISCELLANEOUS, YamlIndicator.NOT),
    YamlTokenType.INTEGER: (YamlCharType.MISCELLANEOUS, YamlIndicator.NOT),
    YamlTokenType.BINARY_INTEGER: (YamlCharType.MISCELLANEOUS, YamlIndicator.NOT),
    YamlTokenType.OCTET_INTEGER: (YamlCharType.MISCELLANEOUS, YamlIndicator.NOT),
    YamlTokenType.HEX_INTEGER: (YamlCharType.MISCELLANEOUS, YamlIndicator.NOT),
    YamlTokenType.FLOAT: (YamlCharType.MISCELLANEOUS, YamlIndicator.NOT),
    YamlTokenType.STRING: (YamlCharType.MISCELLANEOUS, YamlIndicator.NOT),
    YamlTokenType.BOOL: (YamlCharType.MISCELLANEOUS, YamlIndicator.NOT),
    YamlTokenType.INFINITY: (YamlCharType.MISCELLANEOUS, YamlIndicator.NOT),
    YamlTokenType.NAN: (YamlCharType.MISCELLANEOUS, YamlIndicator.NOT),
    YamlTokenType.MAPPING_VALUE: (YamlCharType.INDICATOR, YamlIndicator.BLOCK_STRUCTURE),
    YamlTokenType.SEQUENCE_ENTRY: (YamlCharType.INDICATOR, YamlIndicator.BLOCK_STRUCTURE),
    YamlTokenType.MAPPING_START: (YamlCharType.INDICATOR, YamlIndicator.FLOW_COLLECTION),
    YamlTokenType.MAPPING_END: (YamlCharType.INDICATOR, YamlIndicator.FLOW_COLLECTION),
    YamlTokenType.SEQUENCE_START: (YamlCharType.INDICATOR, YamlIndicator.FLOW_COLLECTION),
    YamlTokenType.SEQUENCE_END: (YamlCharType.INDICATOR, YamlIndicator.FLOW_COLLECTION),
    YamlTokenType.COLLECT_ENTRY: (YamlCharType.INDICATOR, YamlIndicator.FLOW_COLLECTION),
    YamlTokenType.SINGLE_QUOTE: (YamlCharType.INDICATOR, YamlIndicator.QUOTED_SCALAR),
    YamlTokenType.DOUBLE_QUOTE: (YamlCharType.INDICATOR, YamlIndicator.QUOTED_SCALAR),
    YamlTokenType.LITERAL: (YamlCharType.INDICATOR, YamlIndicator.BLOCK_SCALAR),
    YamlTokenType.FOLDED: (YamlCharType.INDICATOR, YamlIndicator.BLOCK_SCALAR),
    YamlTokenType.TAG: (YamlCharType.INDICATOR, YamlIndicator.NODE_PROPERTY),
    YamlTokenType.COMMENT: (YamlCharType.INDICATOR, YamlIndicator.COMMENT),
}


class TokenizeTest(unittest.TestCase):
    # Cases are (yaml, [(type, value, origin), ...]).
    CASES: ta.ClassVar = [
        ('null\n  ', [
            (YamlTokenType.NULL, 'null', 'null\n  '),
        ]),
        ('0_', [
            (YamlTokenType.INTEGER, '0_', '0_'),
        ]),
        ('"hello\\tworld"', [
            (YamlTokenType.DOUBLE_QUOTE, 'hello\tworld', '"hello\\tworld"'),
        ]),
        ('0x_1A_2B_3C', [
            (YamlTokenType.HEX_INTEGER, '0x_1A_2B_3C', '0x_1A_2B_3C'),
        ]),
        ('+0b1010', [
            (YamlTokenType.BINARY_INTEGER, '+0b1010', '+0b1010'),
        ]),
        ('0100', [
            (YamlTokenType.OCTET_INTEGER, '0100', '0100'),
        ]),
        ('0o10', [
            (YamlTokenType.OCTET_INTEGER, '0o10', '0o10'),
        ]),
        ('0.123e+123', [
            (YamlTokenType.FLOAT, '0.123e+123', '0.123e+123'),
        ]),
        ('{}\n  ', [
            (YamlTokenType.MAPPING_START, '{', '{'),
            (YamlTokenType.MAPPING_END, '}', '}'),
        ]),
        ('v: hi', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'hi', ' hi'),
        ]),
        ('v:\ta', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'a', '\ta'),
        ]),
        ('v: "true"', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.DOUBLE_QUOTE, 'true', ' "true"'),
        ]),
        ('v: "false"', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.DOUBLE_QUOTE, 'false', ' "false"'),
        ]),
        ('v: true', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.BOOL, 'true', ' true'),
        ]),
        ('v: false', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.BOOL, 'false', ' false'),
        ]),
        ('v: 10', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INTEGER, '10', ' 10'),
        ]),
        ('v: -10', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INTEGER, '-10', ' -10'),
        ]),
        ('v: 42', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INTEGER, '42', ' 42'),
        ]),
        ('v: 4294967296', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INTEGER, '4294967296', ' 4294967296'),
        ]),
        ('v: "10"', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.DOUBLE_QUOTE, '10', ' "10"'),
        ]),
        ('v: 0.1', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FLOAT, '0.1', ' 0.1'),
        ]),
        ('v: 0.99', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FLOAT, '0.99', ' 0.99'),
        ]),
        ('v: -0.1', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FLOAT, '-0.1', ' -0.1'),
        ]),
        ('v: .inf', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INFINITY, '.inf', ' .inf'),
        ]),
        ('v: -.inf', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INFINITY, '-.inf', ' -.inf'),
        ]),
        ('v: .nan', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.NAN, '.nan', ' .nan'),
        ]),
        ('\na:\n  "bbb  \\\n      ccc\n\n      ddd eee\\n\\\n  \\ \\ fff ggg\\nhhh iii\\n\n  jjj kkk\n  "\n', [
            (YamlTokenType.STRING, 'a', '\na'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (
                YamlTokenType.DOUBLE_QUOTE,
                'bbb  ccc\nddd eee\n  fff ggg\nhhh iii\n jjj kkk ',
                '\n  "bbb  \\\n      ccc\n\n      ddd eee\\n\\\n  \\ \\ fff ggg\\nhhh iii\\n\n  jjj kkk\n  "',
            ),
        ]),
        ('v: null', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.NULL, 'null', ' null'),
        ]),
        ('v: ""', [
            (YamlTokenType.STRING, 'v', 'v'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.DOUBLE_QUOTE, '', ' ""'),
        ]),
        ('\nv:\n- A\n- B\n', [
            (YamlTokenType.STRING, 'v', '\nv'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.SEQUENCE_ENTRY, '-', '\n-'),
            (YamlTokenType.STRING, 'A', ' A\n'),
            (YamlTokenType.SEQUENCE_ENTRY, '-', '-'),
            (YamlTokenType.STRING, 'B', ' B'),
        ]),
        ('\nv:\n- A\n- |-\n B\n C\n', [
            (YamlTokenType.STRING, 'v', '\nv'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.SEQUENCE_ENTRY, '-', '\n-'),
            (YamlTokenType.STRING, 'A', ' A\n'),
            (YamlTokenType.SEQUENCE_ENTRY, '-', '-'),
            (YamlTokenType.LITERAL, '|-', ' |-\n'),
            (YamlTokenType.STRING, 'B\nC', ' B\n C\n'),
        ]),
        ('\nv:\n- A\n- 1\n- B:\n - 2\n - 3\n', [
            (YamlTokenType.STRING, 'v', '\nv'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.SEQUENCE_ENTRY, '-', '\n-'),
            (YamlTokenType.STRING, 'A', ' A\n'),
            (YamlTokenType.SEQUENCE_ENTRY, '-', '-'),
            (YamlTokenType.INTEGER, '1', ' 1\n'),
            (YamlTokenType.SEQUENCE_ENTRY, '-', '-'),
            (YamlTokenType.STRING, 'B', ' B'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.SEQUENCE_ENTRY, '-', '\n -'),
            (YamlTokenType.INTEGER, '2', ' 2\n '),
            (YamlTokenType.SEQUENCE_ENTRY, '-', '-'),
            (YamlTokenType.INTEGER, '3', ' 3'),
        ]),
        ('\na:\n b: c\n', [
            (YamlTokenType.STRING, 'a', '\na'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'b', '\n b'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'c', ' c'),
        ]),
        ("a: '-'", [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.SINGLE_QUOTE, '-', " '-'"),
        ]),
        ('123', [
            (YamlTokenType.INTEGER, '123', '123'),
        ]),
        ('hello: world\n', [
            (YamlTokenType.STRING, 'hello', 'hello'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'world', ' world'),
        ]),
        ('a: null', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.NULL, 'null', ' null'),
        ]),
        ('a: {x: 1}', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.MAPPING_START, '{', ' {'),
            (YamlTokenType.STRING, 'x', 'x'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INTEGER, '1', ' 1'),
            (YamlTokenType.MAPPING_END, '}', '}'),
        ]),
        ('a: [1, 2]', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.SEQUENCE_START, '[', ' ['),
            (YamlTokenType.INTEGER, '1', '1'),
            (YamlTokenType.COLLECT_ENTRY, ',', ','),
            (YamlTokenType.INTEGER, '2', ' 2'),
            (YamlTokenType.SEQUENCE_END, ']', ']'),
        ]),
        ('\nt2: 2018-01-09T10:40:47Z\nt4: 2098-01-09T10:40:47Z\n', [
            (YamlTokenType.STRING, 't2', '\nt2'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, '2018-01-09T10:40:47Z', ' 2018-01-09T10:40:47Z\n'),
            (YamlTokenType.STRING, 't4', 't4'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, '2098-01-09T10:40:47Z', ' 2098-01-09T10:40:47Z'),
        ]),
        ('a: {b: c, d: e}', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.MAPPING_START, '{', ' {'),
            (YamlTokenType.STRING, 'b', 'b'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'c', ' c'),
            (YamlTokenType.COLLECT_ENTRY, ',', ','),
            (YamlTokenType.STRING, 'd', ' d'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'e', ' e'),
            (YamlTokenType.MAPPING_END, '}', '}'),
        ]),
        ('a: 3s', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, '3s', ' 3s'),
        ]),
        ('a: <foo>', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, '<foo>', ' <foo>'),
        ]),
        ('a: "1:1"', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.DOUBLE_QUOTE, '1:1', ' "1:1"'),
        ]),
        ('a: "\\0"', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.DOUBLE_QUOTE, '\x00', ' "\\0"'),
        ]),
        ('a: !!binary gIGC', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.TAG, '!!binary', ' !!binary '),
            (YamlTokenType.STRING, 'gIGC', 'gIGC'),
        ]),
        (
            '\na: !!binary |\n'
            ' kJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJ\n CQ\n',
            [
                (YamlTokenType.STRING, 'a', '\na'),
                (YamlTokenType.MAPPING_VALUE, ':', ':'),
                (YamlTokenType.TAG, '!!binary', ' !!binary '),
                (YamlTokenType.LITERAL, '|', '|\n'),
                (
                    YamlTokenType.STRING,
                    'kJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJ\nCQ\n',
                    ' kJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJ\n CQ\n',
                ),
            ],
        ),
        ('\nb: 2\na: 1\nd: 4\nc: 3\nsub:\n  e: 5\n', [
            (YamlTokenType.STRING, 'b', '\nb'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INTEGER, '2', ' 2\n'),
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INTEGER, '1', ' 1\n'),
            (YamlTokenType.STRING, 'd', 'd'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INTEGER, '4', ' 4\n'),
            (YamlTokenType.STRING, 'c', 'c'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INTEGER, '3', ' 3\n'),
            (YamlTokenType.STRING, 'sub', 'sub'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'e', '\n  e'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.INTEGER, '5', ' 5'),
        ]),
        ('a: 1.2.3.4', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, '1.2.3.4', ' 1.2.3.4'),
        ]),
        ('a: "2015-02-24T18:19:39Z"', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.DOUBLE_QUOTE, '2015-02-24T18:19:39Z', ' "2015-02-24T18:19:39Z"'),
        ]),
        ("a: 'b: c'", [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.SINGLE_QUOTE, 'b: c', " 'b: c'"),
        ]),
        ("a: 'Hello #comment'", [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.SINGLE_QUOTE, 'Hello #comment', " 'Hello #comment'"),
        ]),
        ('a: 100.5', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FLOAT, '100.5', ' 100.5'),
        ]),
        ('a: bogus', [
            (YamlTokenType.STRING, 'a', 'a'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'bogus', ' bogus'),
        ]),
        ('"a": double quoted map key', [
            (YamlTokenType.DOUBLE_QUOTE, 'a', '"a"'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'double quoted map key', ' double quoted map key'),
        ]),
        ("'a': single quoted map key", [
            (YamlTokenType.SINGLE_QUOTE, 'a', "'a'"),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'single quoted map key', ' single quoted map key'),
        ]),
        ('\na: "double quoted"\nb: "value map"', [
            (YamlTokenType.STRING, 'a', '\na'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.DOUBLE_QUOTE, 'double quoted', ' "double quoted"'),
            (YamlTokenType.STRING, 'b', '\nb'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.DOUBLE_QUOTE, 'value map', ' "value map"'),
        ]),
        ("\na: 'single quoted'\nb: 'value map'", [
            (YamlTokenType.STRING, 'a', '\na'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.SINGLE_QUOTE, 'single quoted', " 'single quoted'"),
            (YamlTokenType.STRING, 'b', '\nb'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.SINGLE_QUOTE, 'value map', " 'value map'"),
        ]),
        ("json: '\\\"expression\\\": \\\"thi:\\\"'", [
            (YamlTokenType.STRING, 'json', 'json'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (
                YamlTokenType.SINGLE_QUOTE,
                '\\"expression\\": \\"thi:\\"',
                " '\\\"expression\\\": \\\"thi:\\\"'",
            ),
        ]),
        ('json: "\\"expression\\": \\"thi:\\""', [
            (YamlTokenType.STRING, 'json', 'json'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (
                YamlTokenType.DOUBLE_QUOTE,
                '"expression": "thi:"',
                ' "\\"expression\\": \\"thi:\\""',
            ),
        ]),
        ('\na:\n b\n\n c\n', [
            (YamlTokenType.STRING, 'a', '\na'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'b\nc', '\n b\n\n c'),
        ]),
        ('\na:   \n b   \n\n  \n c\n d \ne: f\n', [
            (YamlTokenType.STRING, 'a', '\na'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'b\nc d', '\n b\n\n\n c\n d\n'),
            (YamlTokenType.STRING, 'e', 'e'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'f', ' f'),
        ]),
        ('\na: |\n b   \n\n  \n c\n d \ne: f\n', [
            (YamlTokenType.STRING, 'a', '\na'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.LITERAL, '|', ' |\n'),
            (YamlTokenType.STRING, 'b   \n\n \nc\nd \n', ' b   \n\n  \n c\n d \n'),
            (YamlTokenType.STRING, 'e', 'e'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'f', ' f'),
        ]),
        ('\na: >\n b   \n\n  \n c\n d \ne: f\n', [
            (YamlTokenType.STRING, 'a', '\na'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FOLDED, '>', ' >\n'),
            (YamlTokenType.STRING, 'b   \n\n \nc d \n', ' b   \n\n  \n c\n d \n'),
            (YamlTokenType.STRING, 'e', 'e'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.STRING, 'f', ' f'),
        ]),
        ('\na: >\n  Text', [
            (YamlTokenType.STRING, 'a', '\na'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FOLDED, '>', ' >\n'),
            (YamlTokenType.STRING, 'Text', '  Text'),
        ]),
        ('\ns: >\n        1s\n', [
            (YamlTokenType.STRING, 's', '\ns'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FOLDED, '>', ' >\n'),
            (YamlTokenType.STRING, '1s\n', '        1s\n'),
        ]),
        ('\ns: >1        # comment\n        1s\n', [
            (YamlTokenType.STRING, 's', '\ns'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FOLDED, '>1', ' >1        '),
            (YamlTokenType.COMMENT, ' comment', '# comment\n'),
            (YamlTokenType.STRING, '       1s\n', '        1s\n'),
        ]),
        ('\ns: >+2\n        1s\n', [
            (YamlTokenType.STRING, 's', '\ns'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FOLDED, '>+2', ' >+2\n'),
            (YamlTokenType.STRING, '      1s\n', '        1s\n'),
        ]),
        ('\ns: >-3\n        1s\n', [
            (YamlTokenType.STRING, 's', '\ns'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FOLDED, '>-3', ' >-3\n'),
            (YamlTokenType.STRING, '     1s', '        1s\n'),
        ]),
        ('\ns: >\n    1s\n    2s\n', [
            (YamlTokenType.STRING, 's', '\ns'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FOLDED, '>', ' >\n'),
            (YamlTokenType.STRING, '1s 2s\n', '    1s\n    2s\n'),
        ]),
        ('\ns: >\n    1s\n      2s\n    3s\n', [
            (YamlTokenType.STRING, 's', '\ns'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FOLDED, '>', ' >\n'),
            (YamlTokenType.STRING, '1s\n  2s\n3s\n', '    1s\n      2s\n    3s\n'),
        ]),
        ('\ns: >\n    1s\n      2s\n      3s\n    4s\n    5s\n', [
            (YamlTokenType.STRING, 's', '\ns'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FOLDED, '>', ' >\n'),
            (YamlTokenType.STRING, '1s\n  2s\n  3s\n4s 5s\n', '    1s\n      2s\n      3s\n    4s\n    5s\n'),
        ]),
        ('\ns: >-3\n    1s\n      2s\n      3s\n    4s\n    5s\n', [
            (YamlTokenType.STRING, 's', '\ns'),
            (YamlTokenType.MAPPING_VALUE, ':', ':'),
            (YamlTokenType.FOLDED, '>-3', ' >-3\n'),
            (YamlTokenType.STRING, ' 1s\n   2s\n   3s\n 4s\n 5s', '    1s\n      2s\n      3s\n    4s\n    5s\n'),
        ]),
        ('\n|2-\n\n                  text\n', [
            (YamlTokenType.LITERAL, '|2-', '\n|2-\n'),
            (YamlTokenType.STRING, '\n                text', '\n                  text\n'),
        ]),
        ('\n|\n  a\n\n\n\n', [
            (YamlTokenType.LITERAL, '|', '\n|\n'),
            (YamlTokenType.STRING, 'a\n', '  a\n\n\n\n'),
        ]),
        ('\n|  \t\t  # comment\n  foo\n', [
            (YamlTokenType.LITERAL, '|', '\n|  \t\t  '),
            (YamlTokenType.COMMENT, ' comment', '# comment\n'),
            (YamlTokenType.STRING, 'foo\n', '  foo\n'),
        ]),
        ('1x0', [
            (YamlTokenType.STRING, '1x0', '1x0'),
        ]),
        ('0b98765', [
            (YamlTokenType.STRING, '0b98765', '0b98765'),
        ]),
        ('098765', [
            (YamlTokenType.STRING, '098765', '098765'),
        ]),
        ('0o98765', [
            (YamlTokenType.STRING, '0o98765', '0o98765'),
        ]),
    ]

    # Faithfully ported cases whose go expectation differs from the python translation's actual output would go here
    # (by CASES index) - never delete or adjust a case to make the suite pass.
    SUSPECTED_DIVERGENCES: ta.ClassVar[ta.List[ta.Any]] = []

    def test_tokenize(self):
        for idx, (src, expected) in enumerate(self.CASES):
            if idx in self.SUSPECTED_DIVERGENCES:
                continue
            with self.subTest(index=idx, yaml=src):
                tokens = yaml_tokenize(src)
                self.assertEqual(len(tokens), len(expected))
                for i, (token_type, value, origin) in enumerate(expected):
                    char_type, indicator = _KINDS[token_type]
                    self.assertEqual(tokens[i].type, token_type)
                    self.assertEqual(tokens[i].char_type, char_type)
                    self.assertEqual(tokens[i].indicator, indicator)
                    self.assertEqual(tokens[i].value, value)
                    self.assertEqual(tokens[i].origin, origin)


class SingleLineTokenPositionTest(unittest.TestCase):
    # Cases are (name, src, {column: value}); every expected token is on line 1.
    CASES: ta.ClassVar = [
        ('single quote, single value array', "test: ['test']", {
            1: 'test',
            5: ':',
            7: '[',
            8: 'test',
            14: ']',
        }),
        ('double quote, single value array', 'test: ["test"]', {
            1: 'test',
            5: ':',
            7: '[',
            8: 'test',
            14: ']',
        }),
        ('no quotes, single value array', 'test: [somevalue]', {
            1: 'test',
            5: ':',
            7: '[',
            8: 'somevalue',
            17: ']',
        }),
        ('single quote, multi value array', "myarr: ['1','2','3', '444' , '55','66' ,  '77'  ]", {
            1: 'myarr',
            6: ':',
            8: '[',
            9: '1',
            12: ',',
            13: '2',
            16: ',',
            17: '3',
            20: ',',
            22: '444',
            28: ',',
            30: '55',
            34: ',',
            35: '66',
            40: ',',
            43: '77',
            49: ']',
        }),
        ('double quote, multi value array', 'myarr: ["1","2","3", "444" , "55","66" ,  "77"  ]', {
            1: 'myarr',
            6: ':',
            8: '[',
            9: '1',
            12: ',',
            13: '2',
            16: ',',
            17: '3',
            20: ',',
            22: '444',
            28: ',',
            30: '55',
            34: ',',
            35: '66',
            40: ',',
            43: '77',
            49: ']',
        }),
        ('no quote, multi value array', 'numbers: [1, 5, 99,100, 3, 7 ]', {
            1: 'numbers',
            8: ':',
            10: '[',
            11: '1',
            12: ',',
            14: '5',
            15: ',',
            17: '99',
            19: ',',
            20: '100',
            23: ',',
            25: '3',
            26: ',',
            28: '7',
            30: ']',
        }),
        ('double quotes, nested arrays', 'Strings: ["1",["2",["3"]]]', {
            1: 'Strings',
            8: ':',
            10: '[',
            11: '1',
            14: ',',
            15: '[',
            16: '2',
            19: ',',
            20: '[',
            21: '3',
            24: ']',
            25: ']',
            26: ']',
        }),
        ('mixed quotes, nested arrays', "Values: [1,['2',\"3\",4,[\"5\",6]]]", {
            1: 'Values',
            7: ':',
            9: '[',
            10: '1',
            11: ',',
            12: '[',
            13: '2',
            16: ',',
            17: '3',
            20: ',',
            21: '4',
            22: ',',
            23: '[',
            24: '5',
            27: ',',
            28: '6',
            29: ']',
            30: ']',
            31: ']',
        }),
        ('double quote, empty array', 'Empty: ["", ""]', {
            1: 'Empty',
            6: ':',
            8: '[',
            9: '',
            11: ',',
            13: '',
            15: ']',
        }),
        ('double quote key', '"a": b', {
            1: 'a',
            4: ':',
            6: 'b',
        }),
        ('single quote key', "'a': b", {
            1: 'a',
            4: ':',
            6: 'b',
        }),
        ('double quote key and value', '"a": "b"', {
            1: 'a',
            4: ':',
            6: 'b',
        }),
        ('single quote key and value', "'a': 'b'", {
            1: 'a',
            4: ':',
            6: 'b',
        }),
        ('double quote key, single quote value', "\"a\": 'b'", {
            1: 'a',
            4: ':',
            6: 'b',
        }),
        ('single quote key, double quote value', "'a': \"b\"", {
            1: 'a',
            4: ':',
            6: 'b',
        }),
    ]

    SUSPECTED_DIVERGENCES: ta.ClassVar[ta.List[ta.Any]] = []

    def test_positions(self):
        for name, src, expect in self.CASES:
            if name in self.SUSPECTED_DIVERGENCES:
                continue
            with self.subTest(name=name):
                got = sorted(yaml_tokenize(src), key=lambda tk: tk.position.column)
                expected = sorted(expect.items())
                self.assertEqual(len(got), len(expected))
                for tk, (column, value) in zip(got, expected):
                    self.assertIsNotNone(tk.position)
                    self.assertEqual(tk.position.line, 1)
                    self.assertEqual(tk.position.column, column)
                    self.assertEqual(tk.value, value)


class MultiLineTokenPositionTest(unittest.TestCase):
    # Cases are (name, src, [(line, column, value), ...]).
    CASES: ta.ClassVar = [
        (
            'double quote',
            'one: "1 2 3 4 5"\ntwo: "1 2\n3 4\n5"\nthree: "1 2 3 4\n5"',
            [
                (1, 1, 'one'),
                (1, 4, ':'),
                (1, 6, '1 2 3 4 5'),
                (2, 1, 'two'),
                (2, 4, ':'),
                (2, 6, '1 2 3 4 5'),
                (5, 1, 'three'),
                (5, 6, ':'),
                (5, 8, '1 2 3 4 5'),
            ],
        ),
        (
            'single quote in an array',
            "arr: ['1', 'and\ntwo']\nlast: 'hello'",
            [
                (1, 1, 'arr'),
                (1, 4, ':'),
                (1, 6, '['),
                (1, 7, '1'),
                (1, 10, ','),
                (1, 12, 'and two'),
                (2, 5, ']'),
                (3, 1, 'last'),
                (3, 5, ':'),
                (3, 7, 'hello'),
            ],
        ),
        (
            'single quote and double quote',
            "foo: \"test\n\n\n\n\nbar\"\nfoo2: 'bar2'",
            [
                (1, 1, 'foo'),
                (1, 4, ':'),
                (1, 6, 'test\n\n\n\nbar'),
                (7, 1, 'foo2'),
                (7, 5, ':'),
                (7, 7, 'bar2'),
            ],
        ),
        (
            'single and double quote map keys',
            "\"a\": test\n'b': 1\nc: true",
            [
                (1, 1, 'a'),
                (1, 4, ':'),
                (1, 6, 'test'),
                (2, 1, 'b'),
                (2, 4, ':'),
                (2, 6, '1'),
                (3, 1, 'c'),
                (3, 2, ':'),
                (3, 4, 'true'),
            ],
        ),
        (
            'issue326',
            'a: |\n  Text\nb: 1',
            [
                (1, 1, 'a'),
                (1, 2, ':'),
                (1, 4, '|'),
                (2, 3, 'Text\n'),
                (3, 1, 'b'),
                (3, 2, ':'),
                (3, 4, '1'),
            ],
        ),
    ]

    SUSPECTED_DIVERGENCES: ta.ClassVar[ta.List[ta.Any]] = []

    def test_positions(self):
        for name, src, expect in self.CASES:
            if name in self.SUSPECTED_DIVERGENCES:
                continue
            with self.subTest(name=name):
                got = sorted(yaml_tokenize(src), key=lambda tk: (tk.position.line, tk.position.column))
                expected = sorted(expect)
                self.assertEqual(len(got), len(expected))
                for tk, (line, column, value) in zip(got, expected):
                    self.assertIsNotNone(tk.position)
                    self.assertEqual(tk.position.line, line)
                    self.assertEqual(tk.position.column, column)
                    self.assertEqual(tk.value, value)


class InvalidTest(unittest.TestCase):
    # Cases are (name, src); each source must produce a stream containing an invalid token.
    CASES: ta.ClassVar = [
        ('literal opt with content', '\na: |invalid\n  foo'),
        ('literal opt', '\na: |invalid'),
        ('invalid single-quoted', "a: 'foobarbaz"),
        ('invalid double-quoted', 'a: "\\"key\\": \\"value:\\"'),
        ('invalid document folded', '>\n>'),
        ('invalid document number', '>\n1'),
        ('invalid document header option number', 'a: >3\n  1'),
        ('use reserved character @', 'key: [@val]'),
        ('use reserved character `', 'key: [`val]'),
        ('use tab character as indent', '\ta: b'),
        ('use tab character as indent in literal', '\na: |\n\tb\n\tc\n'),
        ('invalid UTF-16 character', '"\\u00"'),
        ('invalid UTF-16 surrogate pair length', '"\\ud800"'),
        ('invalid UTF-16 low surrogate prefix', '"\\ud800\\v"'),
        ('invalid UTF-16 low surrogate', '"\\ud800\\u0000"'),
        ('invalid UTF-32 character', '"\\U0000"'),
    ]

    SUSPECTED_DIVERGENCES: ta.ClassVar[ta.List[ta.Any]] = []

    def test_invalid(self):
        for name, src in self.CASES:
            if name in self.SUSPECTED_DIVERGENCES:
                continue
            with self.subTest(name=name):
                got = yaml_tokenize(src)
                self.assertIsNotNone(got.invalid_token())


class TokenOffsetTest(unittest.TestCase):
    def test_crlf(self):
        content = 'project:\r\n  version: 1.2.3\r\n'
        tokens = yaml_tokenize(content)
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[4].value, '1.2.3')
        self.assertEqual(tokens[4].position.offset, 22)

    def test_lf(self):
        content = 'project:\n  version: 1.2.3\n'
        tokens = yaml_tokenize(content)
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[4].value, '1.2.3')
        self.assertEqual(tokens[4].position.offset, 21)


if __name__ == '__main__':
    unittest.main()
