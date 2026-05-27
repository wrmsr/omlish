"""
Inline HTML scanner.

CommonMark §6.6: an inline HTML span is one of

  - open tag:    `<TAGNAME attrs />?`
  - close tag:   `</TAGNAME>`
  - comment:     `<!-- ... -->`
  - PI:          `<? ... ?>`
  - declaration: `<!UPPER ... >`
  - CDATA:       `<![CDATA[ ... ]]>`

Returns the byte span (start..end) of the entire inline-HTML span if one starts at `start`. The caller emits an
`InlineHtml` event with the raw text.

This scanner is also reused to detect HTML block type 7: any complete tag followed only by whitespace until end-of-line.
See pulldown-cmark/src/scanners.rs::{scan_inline_html_*, scan_html_type_7}.
"""
import re

from omlish import dataclasses as dc


##


_RE_TAG_NAME = re.compile(r'[A-Za-z][A-Za-z0-9-]*')
_RE_ATTR_NAME = re.compile(r'[A-Za-z_:][A-Za-z0-9_.:-]*')


@dc.dataclass(frozen=True)
class InlineHtmlMatch:
    end: int     # one past the closing `>` (or `]]>` etc.)


# pulldown-cmark/src/scanners.rs::scan_inline_html (the union of all forms)
def scan_inline_html(text: str, start: int) -> InlineHtmlMatch | None:
    n = len(text)
    if start >= n or text[start] != '<':
        return None
    # Try fixed-prefix forms first.
    if text.startswith('<!--', start):
        return _scan_comment(text, start)
    if text.startswith('<?', start):
        return _scan_pi(text, start)
    if text.startswith('<![CDATA[', start):
        return _scan_cdata(text, start)
    if text.startswith('<!', start):
        return _scan_declaration(text, start)
    if text.startswith('</', start):
        return _scan_close_tag(text, start)
    return _scan_open_tag(text, start)


# comments


def _scan_comment(text: str, start: int) -> InlineHtmlMatch | None:
    # `<!-- ... -->` - body may NOT contain `--` or end with `-`.
    body_start = start + 4
    end = text.find('-->', body_start)
    if end < 0:
        return None
    body = text[body_start:end]
    if body.startswith(('>', '->')):
        return None
    if '--' in body:
        return None
    if body.endswith('-'):
        return None
    return InlineHtmlMatch(end=end + 3)


# processing instruction


def _scan_pi(text: str, start: int) -> InlineHtmlMatch | None:
    end = text.find('?>', start + 2)
    if end < 0:
        return None
    return InlineHtmlMatch(end=end + 2)


# declaration


def _scan_declaration(text: str, start: int) -> InlineHtmlMatch | None:
    # `<!` followed by an ASCII letter, then any chars, then `>`.
    if start + 2 >= len(text):
        return None
    c = text[start + 2]
    if not (c.isascii() and c.isalpha()):
        return None
    end = text.find('>', start + 3)
    if end < 0:
        return None
    return InlineHtmlMatch(end=end + 1)


# CDATA


def _scan_cdata(text: str, start: int) -> InlineHtmlMatch | None:
    end = text.find(']]>', start + 9)
    if end < 0:
        return None
    return InlineHtmlMatch(end=end + 3)


# close tag


def _scan_close_tag(text: str, start: int) -> InlineHtmlMatch | None:
    i = start + 2
    n = len(text)
    m = _RE_TAG_NAME.match(text, i)
    if m is None:
        return None
    i = m.end()
    # Optional whitespace.
    while i < n and text[i] in ' \t\n':
        i += 1
    if i >= n or text[i] != '>':
        return None
    return InlineHtmlMatch(end=i + 1)


# open tag


def _scan_open_tag(text: str, start: int) -> InlineHtmlMatch | None:
    n = len(text)
    i = start + 1
    m = _RE_TAG_NAME.match(text, i)
    if m is None:
        return None
    i = m.end()

    # Zero or more attributes.
    while True:
        save = i
        if not _scan_attribute_ws(text, i):
            break

        # Now consume the attribute itself, if any.
        i_after_ws = _consume_ws_inline(text, i)
        attr_m = _RE_ATTR_NAME.match(text, i_after_ws)
        if attr_m is None:
            i = save
            break
        i = attr_m.end()

        # Optional `= value`.
        j = _consume_ws_inline(text, i)
        if j < n and text[j] == '=':
            j += 1
            j = _consume_ws_inline(text, j)
            val = _scan_attr_value(text, j)
            if val is None:
                # `=` requires a value; this tag is malformed.
                return None
            i = val

    # Optional self-close `/`.
    j = _consume_ws_inline(text, i)
    if j < n and text[j] == '/':
        j += 1
    if j < n and text[j] == '>':
        return InlineHtmlMatch(end=j + 1)

    return None


def _scan_attribute_ws(text: str, i: int) -> bool:
    n = len(text)
    if i >= n:
        return False
    return text[i] in ' \t\n'


def _consume_ws_inline(text: str, i: int) -> int:
    n = len(text)
    while i < n and text[i] in ' \t\n':
        i += 1
    return i


def _scan_attr_value(text: str, i: int) -> int | None:
    n = len(text)
    if i >= n:
        return None
    c = text[i]
    if c == '"' or c == "'":
        # Quoted: any char until matching quote.
        j = text.find(c, i + 1)
        if j < 0:
            return None
        return j + 1
    # Unquoted: any non-whitespace, non-special.
    j = i
    while j < n and text[j] not in ' \t\n"\'=<>`':
        j += 1
    if j == i:
        return None
    return j
