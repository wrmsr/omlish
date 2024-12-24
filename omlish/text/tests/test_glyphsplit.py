# ruff: noqa: PT009
# @omlish-lite
import unittest

from ..glyphsplit import GlyphSplitMatch
from ..glyphsplit import glyph_split_braces


class TestGlyphSplit(unittest.TestCase):
    def test_glyph_split(self):
        self.assertEqual(
            glyph_split_braces('foo {hi} bar {bye[} {{q}} baz'),
            [
                'foo ',
                GlyphSplitMatch('{', 'hi', '}'),
                ' bar ',
                GlyphSplitMatch('{', 'bye[', '}'),
                ' {q} baz',
            ],
        )
