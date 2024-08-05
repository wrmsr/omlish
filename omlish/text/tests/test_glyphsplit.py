from ..glyphsplit import GlyphMatch
from ..glyphsplit import split_braces


def test_glyph_split():
    assert split_braces('foo {hi} bar {bye[} {{q}} baz') == [
        'foo ',
        GlyphMatch('{', 'hi', '}'),
        ' bar ',
        GlyphMatch('{', 'bye[', '}'),
        ' {q} baz',
    ]
