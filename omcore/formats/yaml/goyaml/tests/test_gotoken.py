# @om-lite
"""
Port of go-yaml's token/token_test.go, plus the portable part of ast/ast_test.go (TestEscapeSingleQuote). Expected
values come from the go test sources verbatim.

Not ported: Tokens.Dump() (untranslated debug helper), and ast_test.go's TestReadNode (the io.Reader translation is a
known-broken FIXME).
"""
import unittest

from .. import tokens as tokens_mod
from ..ast import _yaml_escape_single_quote  # noqa
from ..tokens import YamlPosition
from ..tokens import YamlTokenMakers
from ..tokens import YamlTokens
from ..tokens import YamlTokenType
from ..tokens import yaml_new_token


def _pos():
    return YamlPosition(line=0, column=0, offset=0, indent_num=0, indent_level=0)


class TokenTest(unittest.TestCase):
    def test_token(self):
        pos = _pos()
        tokens = YamlTokens()
        for tk in [
            YamlTokenMakers.new_sequence_entry('-', pos),
            YamlTokenMakers.new_mapping_key(pos),
            YamlTokenMakers.new_mapping_value(pos),
            YamlTokenMakers.new_collect_entry(',', pos),
            YamlTokenMakers.new_sequence_start('[', pos),
            YamlTokenMakers.new_sequence_end(']', pos),
            YamlTokenMakers.new_mapping_start('{', pos),
            YamlTokenMakers.new_mapping_end('}', pos),
            YamlTokenMakers.new_comment('#', '#', pos),
            YamlTokenMakers.new_anchor('&', pos),
            YamlTokenMakers.new_alias('*', pos),
            YamlTokenMakers.new_literal('|', '|', pos),
            YamlTokenMakers.new_folded('>', '>', pos),
            YamlTokenMakers.new_single_quote("'", "'", pos),
            YamlTokenMakers.new_double_quote('"', '"', pos),
            YamlTokenMakers.new_directive('%', pos),
            YamlTokenMakers.new_space(pos),
            YamlTokenMakers.new_merge_key('<<', pos),
            YamlTokenMakers.new_document_header('---', pos),
            YamlTokenMakers.new_document_end('...', pos),
            yaml_new_token('1', '1', pos),
            yaml_new_token('3.14', '3.14', pos),
            yaml_new_token('-0b101010', '-0b101010', pos),
            yaml_new_token('0xA', '0xA', pos),
            yaml_new_token('685.230_15e+03', '685.230_15e+03', pos),
            yaml_new_token('02472256', '02472256', pos),
            yaml_new_token('0o2472256', '0o2472256', pos),
            yaml_new_token('', '', pos),
            yaml_new_token('_1', '_1', pos),
            yaml_new_token('1.1.1.1', '1.1.1.1', pos),
            yaml_new_token('+', '+', pos),
            yaml_new_token('-', '-', pos),
            yaml_new_token('_', '_', pos),
            yaml_new_token('~', '~', pos),
            yaml_new_token('true', 'true', pos),
            yaml_new_token('false', 'false', pos),
            yaml_new_token('.nan', '.nan', pos),
            yaml_new_token('.inf', '.inf', pos),
            yaml_new_token('-.inf', '-.inf', pos),
            yaml_new_token('null', 'null', pos),
            YamlTokenMakers.new_tag('!!null', '!!null', pos),
            YamlTokenMakers.new_tag('!!map', '!!map', pos),
            YamlTokenMakers.new_tag('!!str', '!!str', pos),
            YamlTokenMakers.new_tag('!!seq', '!!seq', pos),
            YamlTokenMakers.new_tag('!!binary', '!!binary', pos),
            YamlTokenMakers.new_tag('!!omap', '!!omap', pos),
            YamlTokenMakers.new_tag('!!set', '!!set', pos),
            YamlTokenMakers.new_tag('!!int', '!!int', pos),
            YamlTokenMakers.new_tag('!!float', '!!float', pos),
            YamlTokenMakers.new_tag('!hoge', '!hoge', pos),
        ]:
            # go builds the Tokens slice as a literal (no linking); mirror with plain appends.
            tokens.append(tk)

        tokens.add(yaml_new_token('hoge', 'hoge', pos))
        self.assertEqual(tokens[len(tokens) - 1].previous_type(), YamlTokenType.TAG)
        self.assertEqual(tokens[0].previous_type(), YamlTokenType.UNKNOWN)
        self.assertEqual(tokens[len(tokens) - 2].next_type(), YamlTokenType.STRING)
        self.assertEqual(tokens[len(tokens) - 1].next_type(), YamlTokenType.UNKNOWN)


class IsNeedQuotedTest(unittest.TestCase):
    def test_need_quoted(self):
        need_quoted_tests = [
            '',
            'true',
            '1.234',
            '0b11111111111111111111111111111111111111111111111111111111111111111',
            '0o7777777777777777777777777777777777777777',
            '999999999999999999999999999999999999999999',
            '0xffffffffffffffffffffffffffffffffffffffff',
            '1:1',
            '2001-12-15T02:59:43.1Z',
            '2001-12-14t21:59:43.10-05:00',
            '2001-12-15 2:59:43.10',
            '2002-12-14',
            'hoge # comment',
            '\\0',
            '#a b',
            '*a b',
            '&a b',
            '{a b',
            '}a b',
            '[a b',
            ']a b',
            ',a b',
            '!a b',
            '|a b',
            '>a b',
            '>a b',
            '%a b',
            "'a b",
            '"a b',
            'a:',
            'a: b',
            'y',
            'Y',
            'yes',
            'Yes',
            'YES',
            'n',
            'N',
            'no',
            'No',
            'NO',
            'on',
            'On',
            'ON',
            'off',
            'Off',
            'OFF',
            '@test',
            ':0',
            ':8080',
            ':value',
            ' a',
            ' a ',
            'a ',
            'null',
            'Null',
            'NULL',
            '~',
            '-',
            '- --foo',
        ]
        for test in need_quoted_tests:
            with self.subTest(test=test):
                self.assertTrue(tokens_mod._yaml_is_need_quoted(test))  # noqa

    def test_not_need_quoted(self):
        not_need_quoted_tests = [
            'Hello World',
            # time.Parse cannot handle: "2001-12-14 21:59:43.10 -5" from the examples.
            # https://yaml.org/type/timestamp.html
            '2001-12-14 21:59:43.10 -5',
        ]
        for test in not_need_quoted_tests:
            with self.subTest(test=test):
                self.assertFalse(tokens_mod._yaml_is_need_quoted(test))  # noqa


class EscapeSingleQuoteTest(unittest.TestCase):
    def test_escape_single_quote(self):
        self.assertEqual(_yaml_escape_single_quote("Victor's victory"), "'Victor''s victory'")


if __name__ == '__main__':
    unittest.main()
