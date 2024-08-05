import dataclasses as dc
import re

from .. import check


@dc.dataclass(frozen=True)
class GlyphMatch:
    l: str
    s: str
    r: str


class GlyphSplitter:

    def __init__(self, glyphs: tuple[str, str]) -> None:
        super().__init__()

        glyphs = tuple(map(check.of_isinstance(str), glyphs))  # type: ignore
        check.state(all(len(s) == 1 for s in glyphs))
        check.state(len(glyphs) == 2)

        self._glyphs = glyphs
        self._lglyph, self._rglyph = glyphs

        self._double_glyphs: tuple[str, str] = tuple(s * 2 for s in glyphs)  # type: ignore  # noqa
        self._escaped_glyphs: tuple[str, str] = tuple(map(re.escape, glyphs))  # type: ignore  # noqa

        self._lglyph_pat = re.compile(r'(%s)' % (self._escaped_glyphs[0] * 2,))  # noqa
        self._rglyph_pat = re.compile(r'(%s)' % (self._escaped_glyphs[1] * 2,))  # noqa
        self._single_glyph_pat = re.compile(r'(%s[^%s]*?%s)' % (  # noqa
            self._escaped_glyphs[0], self._escaped_glyphs[1], self._escaped_glyphs[1]))

    def split(self, s: str) -> list[GlyphMatch | str]:
        ps = self._lglyph_pat.split(s)
        ps = [p[::-1] for p in ps for p in reversed(self._rglyph_pat.split(p[::-1]))]

        lst = []
        for p in ps:
            if p in self._double_glyphs:
                lst.append(p)
                continue

            ms = list(self._single_glyph_pat.finditer(p))
            if not ms:
                lst.append(p)
                continue

            l = 0
            for m in ms:
                if m.start() != l:
                    lst.append(p[l:m.start()])
                lst.append(GlyphMatch(self._lglyph, p[m.start() + 1:m.end() - 1], self._rglyph))
                l = m.end()

            if l < len(p):
                lst.append(p[l:])

        return lst


_PAREN_GLYPH_SPLITTER = GlyphSplitter(('(', ')'))
_BRACE_GLYPH_SPLITTER = GlyphSplitter(('{', '}'))
_BRACKET_GLYPH_SPLITTER = GlyphSplitter(('[', ']'))
_ANGLE_BRACKET_GLYPH_SPLITTER = GlyphSplitter(('<', '>'))

split_parens = _PAREN_GLYPH_SPLITTER.split
split_braces = _BRACE_GLYPH_SPLITTER.split
split_brackets = _BRACKET_GLYPH_SPLITTER.split
split_angle_brackets = _ANGLE_BRACKET_GLYPH_SPLITTER.split
