"""
Note: string.Formatter (and string.Template) shouldn't be ignored - if they can be used they probably should be.
 - https://docs.python.org/3/library/string.html#custom-string-formatting
 - https://docs.python.org/3/library/string.html#template-strings
"""
import dataclasses as dc
import re

from .. import check


@dc.dataclass(frozen=True)
class GlyphMatch:
    l: str
    s: str
    r: str


class GlyphSplitter:

    def __init__(
            self,
            glyphs: tuple[str, str],
            *,
            escape_returned_doubles: bool = False,
            compact: bool = False,
    ) -> None:
        super().__init__()

        glyphs = tuple(map(check.of_isinstance(str), glyphs))  # type: ignore
        check.state(all(len(s) == 1 for s in glyphs))
        check.state(len(glyphs) == 2)

        self._glyphs = glyphs
        self._l_glyph, self._r_glyph = glyphs

        self._escape_returned_doubles = escape_returned_doubles
        self._compact = compact

        self._l_double_glyph = self._l_glyph * 2
        self._r_double_glyph = self._r_glyph * 2
        self._double_glyphs = (self._l_double_glyph, self._r_double_glyph)

        self._l_escaped_glyph = re.escape(self._l_glyph)
        self._r_escaped_glyph = re.escape(self._r_glyph)

        self._l_glyph_pat = re.compile(r'(%s)' % (self._l_escaped_glyph * 2,))  # noqa
        self._r_glyph_pat = re.compile(r'(%s)' % (self._r_escaped_glyph * 2,))  # noqa

        self._single_glyph_pat = re.compile(r'(%s[^%s]*?%s)' % (self._l_escaped_glyph, self._r_escaped_glyph, self._r_escaped_glyph))  # noqa

    def split(self, s: str) -> list[GlyphMatch | str]:
        ps = self._l_glyph_pat.split(s)
        ps = [p[::-1] for p in ps for p in reversed(self._r_glyph_pat.split(p[::-1]))]

        ret = []  # type: ignore

        def append_ret(o):
            if self._compact and isinstance(o, str) and ret and isinstance(ret[-1], str):
                ret[-1] = ret[-1] + o
            else:
                ret.append(o)

        for p in ps:
            if p in self._double_glyphs:
                if self._escape_returned_doubles:
                    p = self._glyphs[p == self._r_double_glyph]
                append_ret(p)
                continue

            ms = list(self._single_glyph_pat.finditer(p))
            if not ms:
                append_ret(p)
                continue

            l = 0
            for m in ms:
                if m.start() != l:
                    append_ret(p[l:m.start()])
                append_ret(GlyphMatch(self._l_glyph, p[m.start() + 1:m.end() - 1], self._r_glyph))
                l = m.end()

            if l < len(p):
                append_ret(p[l:])

        return ret


_PAREN_GLYPH_SPLITTER = GlyphSplitter(('(', ')'), escape_returned_doubles=True, compact=True)
_BRACE_GLYPH_SPLITTER = GlyphSplitter(('{', '}'), escape_returned_doubles=True, compact=True)
_BRACKET_GLYPH_SPLITTER = GlyphSplitter(('[', ']'), escape_returned_doubles=True, compact=True)
_ANGLE_BRACKET_GLYPH_SPLITTER = GlyphSplitter(('<', '>'), escape_returned_doubles=True, compact=True)

split_parens = _PAREN_GLYPH_SPLITTER.split
split_braces = _BRACE_GLYPH_SPLITTER.split
split_brackets = _BRACKET_GLYPH_SPLITTER.split
split_angle_brackets = _ANGLE_BRACKET_GLYPH_SPLITTER.split
