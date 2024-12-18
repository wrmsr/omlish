# ruff: noqa: PT009 UP007
import unittest

from ..shlex import shlex_maybe_quote


class TestShlex(unittest.TestCase):
    def test_shlex_maybe_quote(self):
        self.assertEqual(shlex_maybe_quote('foo'), 'foo')
        self.assertEqual(shlex_maybe_quote('"foo"'), '"foo"')
        self.assertEqual(shlex_maybe_quote("'foo'"), "'foo'")

        self.assertEqual(shlex_maybe_quote('foo bar'), "'foo bar'")
        self.assertEqual(shlex_maybe_quote('"foo bar"'), '"foo bar"')
        self.assertEqual(shlex_maybe_quote("'foo bar'"), "'foo bar'")

        self.assertEqual(shlex_maybe_quote('foo bar'), "'foo bar'")
        self.assertEqual(shlex_maybe_quote('"foo bar" foo'), '\'"foo bar" foo\'')
        self.assertEqual(shlex_maybe_quote("'foo bar' foo"), '\'\'"\'"\'foo bar\'"\'"\' foo\'')
