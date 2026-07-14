"""
HTML entity reference scanner.

CommonMark §6.2: three entity forms,

  * named: `&name;`            (e.g. `&copy;`)
  * decimal: `&#NNNN;`         (e.g. `&#35;` → `#`)
  * hexadecimal: `&#xHHHH;` / `&#XHHHH;`

We delegate decoding to stdlib `html.unescape`, which has the full HTML5 named-entity table - far larger and more
current than pulldown-cmark's generated 2125-row `entities.rs`. The job here is just to recognize the byte span of a
valid entity reference and decode it.
"""
import html
import re

from omcore import dataclasses as dc


##


# CM-spec entity shapes. Note: numeric forms must have 1..7 digits and must be followed by `;`.
_RE_NAMED = re.compile(r'&([A-Za-z][A-Za-z0-9]{0,31});')
_RE_DECIMAL = re.compile(r'&#([0-9]{1,7});')
_RE_HEX = re.compile(r'&#[xX]([0-9A-Fa-f]{1,6});')


@dc.dataclass(frozen=True)
class EntityMatch:
    end: int      # one past the closing `;`
    decoded: str  # the decoded character(s); falls back to the raw text for unknown named refs


# pulldown-cmark/src/scanners.rs::scan_entity - same shape but we lean on stdlib `html.unescape`.
def scan_entity(text: str, start: int) -> EntityMatch | None:
    if start >= len(text) or text[start] != '&':
        return None

    # Try each form in fixed precedence: hex (most specific), then decimal, then named.
    m = _RE_HEX.match(text, start)
    if m is not None:
        code = int(m.group(1), 16)
        if not _is_valid_codepoint(code):
            return EntityMatch(end=m.end(), decoded='�')
        return EntityMatch(end=m.end(), decoded=chr(code))

    m = _RE_DECIMAL.match(text, start)
    if m is not None:
        code = int(m.group(1))
        if not _is_valid_codepoint(code):
            return EntityMatch(end=m.end(), decoded='�')
        return EntityMatch(end=m.end(), decoded=chr(code))

    m = _RE_NAMED.match(text, start)
    if m is not None:
        # `html.unescape` resolves all HTML5 named entities; for unknown names it returns the input unchanged (which is
        # the wrong behavior - CM says unknown named refs render as plain text). We detect by comparing.
        raw = m.group(0)
        decoded = html.unescape(raw)
        if decoded == raw:
            return None
        return EntityMatch(end=m.end(), decoded=decoded)

    return None


def _is_valid_codepoint(code: int) -> bool:
    # Per CM §6.2: NUL is forbidden; values out of the Unicode range fall back to U+FFFD.
    if code == 0:
        return False
    if code > 0x10FFFF:
        return False
    # Surrogates are also invalid.
    if 0xD800 <= code <= 0xDFFF:
        return False
    return True
