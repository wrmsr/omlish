# ruff: noqa: PT009
# @omlish-lite
import functools
import unittest

from ..glyphsplit import GlyphSplitMatch
from ..glyphsplit import glyph_split_braces
from ..glyphsplit import glyph_split_interpolate


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

    def test_interpolate(self):
        fn = functools.partial(
            glyph_split_interpolate,
            glyph_split_braces,
            dict(
                hi='hi!',
                bye='bye?',
            ),
        )

        self.assertEqual(
            fn('foo {hi} bar {bye} baz'),
            'foo hi! bar bye? baz',
        )
