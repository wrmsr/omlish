# @omlish-lite
# ruff: noqa: PT009 UP006 UP007
# Copyright (c) 2017 Anthony Sottile
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# https://github.com/asottile/tokenize-rt/blob/413692b7c1ad8a873caec39dd4f427d55ee538ea/tests/tokenize_rt_test.py
import re
import sys
import unittest

from ..tokenizert import Token
from ..tokenizert import Tokenization
from ..tokenizert import TokenNames
from ..tokenizert import TokenOffset


class TestTokenizert(unittest.TestCase):
    def test_re_partition_no_match(self):
        ret = Tokenization._re_partition(re.compile('z'), 'abc')  # noqa
        self.assertEqual(ret, ('abc', '', ''))

    def test_re_partition_match(self):
        ret = Tokenization._re_partition(re.compile('b'), 'abc')  # noqa
        self.assertEqual(ret, ('a', 'b', 'c'))

    def test_offset_default_values(self):
        self.assertEqual(TokenOffset(), TokenOffset(line=None, utf8_byte_offset=None))

    def test_token_offset(self):
        token = Token('NAME', 'x', line=1, utf8_byte_offset=2)
        self.assertEqual(token.offset, TokenOffset(line=1, utf8_byte_offset=2))

    def test_token_matches(self):
        token = Token('NAME', 'x', line=1, utf8_byte_offset=2)
        self.assertTrue(token.matches(name='NAME', src='x'))
        self.assertFalse(token.matches(name='OP', src='x'))
        self.assertFalse(token.matches(name='NAME', src='y'))
        self.assertFalse(token.matches(name='OP', src=':'))

    def test_src_to_tokens_simple(self):
        src = 'x = 5\n'
        ret = Tokenization.src_to_tokens(src)
        self.assertEqual(ret, [
            Token('NAME', 'x', line=1, utf8_byte_offset=0),
            Token(TokenNames.UNIMPORTANT_WS, ' ', line=1, utf8_byte_offset=1),
            Token('OP', '=', line=1, utf8_byte_offset=2),
            Token(TokenNames.UNIMPORTANT_WS, ' ', line=1, utf8_byte_offset=3),
            Token('NUMBER', '5', line=1, utf8_byte_offset=4),
            Token('NEWLINE', '\n', line=1, utf8_byte_offset=5),
            Token('ENDMARKER', '', line=2, utf8_byte_offset=0),
        ])

    def test_src_to_tokens_escaped_nl(self):
        src = (
            'x = \\\n'
            '    5\n'
        )
        ret = Tokenization.src_to_tokens(src)
        self.assertEqual(ret, [
            Token('NAME', 'x', line=1, utf8_byte_offset=0),
            Token(TokenNames.UNIMPORTANT_WS, ' ', line=1, utf8_byte_offset=1),
            Token('OP', '=', line=1, utf8_byte_offset=2),
            Token(TokenNames.UNIMPORTANT_WS, ' ', line=1, utf8_byte_offset=3),
            Token(TokenNames.ESCAPED_NL, '\\\n', line=1, utf8_byte_offset=4),
            Token(TokenNames.UNIMPORTANT_WS, '    ', line=2, utf8_byte_offset=0),
            Token('NUMBER', '5', line=2, utf8_byte_offset=4),
            Token('NEWLINE', '\n', line=2, utf8_byte_offset=5),
            Token('ENDMARKER', '', line=3, utf8_byte_offset=0),
        ])

    def test_src_to_tokens_escaped_nl_no_left_ws(self):
        src = (
            'x =\\\n'
            '    5\n'
        )
        ret = Tokenization.src_to_tokens(src)
        self.assertEqual(ret, [
            Token('NAME', 'x', line=1, utf8_byte_offset=0),
            Token(TokenNames.UNIMPORTANT_WS, ' ', line=1, utf8_byte_offset=1),
            Token('OP', '=', line=1, utf8_byte_offset=2),
            Token(TokenNames.ESCAPED_NL, '\\\n', line=1, utf8_byte_offset=3),
            Token(TokenNames.UNIMPORTANT_WS, '    ', line=2, utf8_byte_offset=0),
            Token('NUMBER', '5', line=2, utf8_byte_offset=4),
            Token('NEWLINE', '\n', line=2, utf8_byte_offset=5),
            Token('ENDMARKER', '', line=3, utf8_byte_offset=0),
        ])

    def test_src_to_tokens_escaped_nl_windows(self):
        src = (
            'x = \\\r\n'
            '    5\r\n'
        )
        ret = Tokenization.src_to_tokens(src)
        self.assertEqual(ret, [
            Token('NAME', 'x', line=1, utf8_byte_offset=0),
            Token(TokenNames.UNIMPORTANT_WS, ' ', line=1, utf8_byte_offset=1),
            Token('OP', '=', line=1, utf8_byte_offset=2),
            Token(TokenNames.UNIMPORTANT_WS, ' ', line=1, utf8_byte_offset=3),
            Token(TokenNames.ESCAPED_NL, '\\\r\n', line=1, utf8_byte_offset=4),
            Token(TokenNames.UNIMPORTANT_WS, '    ', line=2, utf8_byte_offset=0),
            Token('NUMBER', '5', line=2, utf8_byte_offset=4),
            Token('NEWLINE', '\r\n', line=2, utf8_byte_offset=5),
            Token('ENDMARKER', '', line=3, utf8_byte_offset=0),
        ])

    def test_src_to_tokens_implicit_continue(self):
        src = (
            'x = (\n'
            '    1,\n'
            '    2,\n'
            ')\n'
        )
        ret = Tokenization.src_to_tokens(src)
        self.assertEqual(ret, [
            Token(name='NAME', src='x', line=1, utf8_byte_offset=0),
            Token(name='UNIMPORTANT_WS', src=' ', line=1, utf8_byte_offset=1),
            Token(name='OP', src='=', line=1, utf8_byte_offset=2),
            Token(name='UNIMPORTANT_WS', src=' ', line=1, utf8_byte_offset=3),
            Token(name='OP', src='(', line=1, utf8_byte_offset=4),
            Token(name='NL', src='\n', line=1, utf8_byte_offset=5),
            Token(name='UNIMPORTANT_WS', src='    ', line=2, utf8_byte_offset=0),
            Token(name='NUMBER', src='1', line=2, utf8_byte_offset=4),
            Token(name='OP', src=',', line=2, utf8_byte_offset=5),
            Token(name='NL', src='\n', line=2, utf8_byte_offset=6),
            Token(name='UNIMPORTANT_WS', src='    ', line=3, utf8_byte_offset=0),
            Token(name='NUMBER', src='2', line=3, utf8_byte_offset=4),
            Token(name='OP', src=',', line=3, utf8_byte_offset=5),
            Token(name='NL', src='\n', line=3, utf8_byte_offset=6),
            Token(name='OP', src=')', line=4, utf8_byte_offset=0),
            Token(name='NEWLINE', src='\n', line=4, utf8_byte_offset=1),
            Token(name='ENDMARKER', src='', line=5, utf8_byte_offset=0),
        ])

    def test_src_to_tokens_no_eol_eof(self):
        ret = Tokenization.src_to_tokens('1')
        self.assertEqual(ret, [
            Token('NUMBER', '1', line=1, utf8_byte_offset=0),
            Token('NEWLINE', '', line=1, utf8_byte_offset=1),
            Token('ENDMARKER', '', line=2, utf8_byte_offset=0),
        ])

    def test_src_to_tokens_multiline_string(self):
        src = (
            'x = """\n'
            '  y\n'
            '""".format(1)\n'
        )
        ret = Tokenization.src_to_tokens(src)
        self.assertEqual(ret, [
            Token(name='NAME', src='x', line=1, utf8_byte_offset=0),
            Token(name='UNIMPORTANT_WS', src=' ', line=1, utf8_byte_offset=1),
            Token(name='OP', src='=', line=1, utf8_byte_offset=2),
            Token(name='UNIMPORTANT_WS', src=' ', line=1, utf8_byte_offset=3),
            Token(name='STRING', src='"""\n  y\n"""', line=1, utf8_byte_offset=4),
            Token(name='OP', src='.', line=3, utf8_byte_offset=3),
            Token(name='NAME', src='format', line=3, utf8_byte_offset=4),
            Token(name='OP', src='(', line=3, utf8_byte_offset=10),
            Token(name='NUMBER', src='1', line=3, utf8_byte_offset=11),
            Token(name='OP', src=')', line=3, utf8_byte_offset=12),
            Token(name='NEWLINE', src='\n', line=3, utf8_byte_offset=13),
            Token(name='ENDMARKER', src='', line=4, utf8_byte_offset=0),
        ])

    def test_src_to_tokens_fstring_with_escapes(self):
        src = 'f" a {{ {b} }} c"'
        ret = Tokenization.src_to_tokens(src)
        if sys.version_info >= (3, 12):  # noqa
            self.assertEqual(ret, [
                Token(name='FSTRING_START', src='f"', line=1, utf8_byte_offset=0),
                Token(name='FSTRING_MIDDLE', src=' a {{', line=1, utf8_byte_offset=2),  # noqa: E501
                Token(name='FSTRING_MIDDLE', src=' ', line=1, utf8_byte_offset=7),
                Token(name='OP', src='{', line=1, utf8_byte_offset=8),
                Token(name='NAME', src='b', line=1, utf8_byte_offset=9),
                Token(name='OP', src='}', line=1, utf8_byte_offset=10),
                Token(name='FSTRING_MIDDLE', src=' }}', line=1, utf8_byte_offset=11),  # noqa: E501
                Token(name='FSTRING_MIDDLE', src=' c', line=1, utf8_byte_offset=14),  # noqa: E501
                Token(name='FSTRING_END', src='"', line=1, utf8_byte_offset=16),
                Token(name='NEWLINE', src='', line=1, utf8_byte_offset=17),
                Token(name='ENDMARKER', src='', line=2, utf8_byte_offset=0),
            ])
        else:
            self.assertEqual(ret, [
                Token(name='STRING', src='f" a {{ {b} }} c"', line=1, utf8_byte_offset=0),  # noqa: E501
                Token(name='NEWLINE', src='', line=1, utf8_byte_offset=17),
                Token(name='ENDMARKER', src='', line=2, utf8_byte_offset=0),
            ])

    def test_src_to_tokens_fstring_with_named_escapes(self):
        src = r'f" \N{SNOWMAN} "'
        ret = Tokenization.src_to_tokens(src)
        if sys.version_info >= (3, 12):  # noqa
            self.assertEqual(ret, [
                Token(name='FSTRING_START', src='f"', line=1, utf8_byte_offset=0),
                Token(name='FSTRING_MIDDLE', src=' \\N{SNOWMAN}', line=1, utf8_byte_offset=2),  # noqa: E501
                Token(name='FSTRING_MIDDLE', src=' ', line=1, utf8_byte_offset=14),
                Token(name='FSTRING_END', src='"', line=1, utf8_byte_offset=15),
                Token(name='NEWLINE', src='', line=1, utf8_byte_offset=16),
                Token(name='ENDMARKER', src='', line=2, utf8_byte_offset=0),
            ])
        else:
            self.assertEqual(ret, [
                Token(name='STRING', src='f" \\N{SNOWMAN} "', line=1, utf8_byte_offset=0),  # noqa: E501
                Token(name='NEWLINE', src='', line=1, utf8_byte_offset=16),
                Token(name='ENDMARKER', src='', line=2, utf8_byte_offset=0),
            ])

    def test_roundtrip_tokenize(self):
        for contents in (
            (
                'from __future__ import annotations\n'
                'x = \\\n'
                '    5\n'
                '\n'
                '# Also with multiple lines of backslashing\n'
                'x = \\\n'
                '    \\\n'
                '    \\\n'
                '    \\\n'
                '    5\n'
            ),
            '',
            (
                'from __future__ import annotations\n'
                "x = '☃'\n"
            ),
        ):
            ret = Tokenization.tokens_to_src(Tokenization.src_to_tokens(contents))
            self.assertEqual(ret, contents)

    def test_parse_string_literal(self):
        for s, expected in (
            ('""', ('', '""')),
            ('u"foo"', ('u', '"foo"')),
            ('F"hi"', ('F', '"hi"')),
            ('r"""x"""', ('r', '"""x"""')),
        ):
            self.assertEqual(Tokenization.parse_string_literal(s), expected)

    def test_rfind_string_parts_only_literal(self):
        for src in ('""', "b''", "r'''.'''"):
            tokens = Tokenization.src_to_tokens(src)
            self.assertEqual(Tokenization.rfind_string_parts(tokens, 0), (0,))

    def test_rfind_string_parts_py312_plus(self):
        # in 3.12 this was changed to have its own tokenization (not as a string)
        tokens = Tokenization.src_to_tokens("f''")
        if sys.version_info >= (3, 12):  # noqa
            self.assertEqual(Tokenization.rfind_string_parts(tokens, 0), ())
        else:
            self.assertEqual(Tokenization.rfind_string_parts(tokens, 0), (0,))

    def test_rfind_string_parts_multiple_tokens(self):
        for src, n, expected in (
            ('"foo" "bar"', 2, (0, 2)),
            ('"""foo""" "bar"', 2, (0, 2)),
            (
                '(\n'
                '    "foo"\n'
                '    "bar"\n'
                ')',
                8,
                (3, 6),
            ),
            (
                'print(\n'
                '    "foo"\n'
                '    "bar"\n'
                ')',
                7,
                (4, 7),
            ),
        ):
            tokens = Tokenization.src_to_tokens(src)
            self.assertEqual(Tokenization.rfind_string_parts(tokens, n), expected)

    def test_rfind_string_parts_not_a_string(self):
        tokens = Tokenization.src_to_tokens('print')
        self.assertEqual(Tokenization.rfind_string_parts(tokens, 0), ())

    def test_rfind_string_parts_end_of_call_looks_like_string(self):
        for src, n in (
            #           v
            ('x(1, "foo")', 6),
            #         v
            ('x ("foo")', 4),
            #           v
            ('x[0]("foo")', 6),
            #           v
            ('x(0)("foo")', 6),
        ):
            tokens = Tokenization.src_to_tokens(src)
            self.assertEqual(Tokenization.rfind_string_parts(tokens, n), ())

    def test_rfind_string_parts_parenthesized(self):
        for src, n, expected_i in (
            #       v
            ('("foo")', 2, 1),
            #           v
            ('((("foo")))', 6, 3),
            #           v
            ('a + ("foo")', 6, 5),
            #            v
            ('a or ("foo")', 6, 5),
        ):
            tokens = Tokenization.src_to_tokens(src)
            self.assertEqual(Tokenization.rfind_string_parts(tokens, n), (expected_i,))

    # def test_main(self, capsys, tmp_path):
    #     f = tmp_path.joinpath('simple.py')
    #     f.write_text('x = 5\n')
    #     main((str(f),))
    #     out, _ = capsys.readouterr()
    #     self.assertEqual(out, (
    #         "1:0 NAME 'x'\n"
    #         "1:1 UNIMPORTANT_WS ' '\n"
    #         "1:2 OP '='\n"
    #         "1:3 UNIMPORTANT_WS ' '\n"
    #         "1:4 NUMBER '5'\n"
    #         "1:5 NEWLINE '\\n'\n"
    #         "2:0 ENDMARKER ''\n"
    #     ))

    def test_curly_escape(self):
        for s, expected in (
            ('', ''),
            ('{foo}', '{{foo}}'),
            (r'\N{SNOWMAN}', r'\N{SNOWMAN}'),
            (r'\N{SNOWMAN} {bar}', r'\N{SNOWMAN} {{bar}}'),
        ):
            self.assertEqual(Tokenization.curly_escape(s), expected)
