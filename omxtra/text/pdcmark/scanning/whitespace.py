"""
Whitespace / EOL / character-class helpers.

Direct ports of the small scanners at the bottom of pulldown-cmark/src/scanners.rs, adapted to work on `str` rather than
`&[u8]`. For pure-ASCII control characters (which is what these test) the operation is identical.

Convention: where pulldown-cmark uses byte indices into `&[u8]`, we use character indices into `str`. For ASCII-only
content the two coincide; for inputs containing non-ASCII characters the character index is what naturally indexes a
Python `str`.
"""


##


# pulldown-cmark/src/scanners.rs::is_ascii_whitespace
def is_ascii_whitespace(c: str) -> bool:
    return c in ' \t\n\v\f\r'


# pulldown-cmark/src/scanners.rs::is_ascii_whitespace_no_nl
def is_ascii_whitespace_no_nl(c: str) -> bool:
    return c in ' \t\v\f'


def is_ascii_punctuation(c: str) -> bool:
    return c in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'


def is_ascii_alphanumeric(c: str) -> bool:
    return c.isascii() and c.isalnum()


# pulldown-cmark/src/scanners.rs::scan_ch
def scan_ch(s: str, i: int, c: str) -> int:
    """1 if `s[i] == c`, else 0."""

    return 1 if i < len(s) and s[i] == c else 0


# pulldown-cmark/src/scanners.rs::scan_ch_repeat
def scan_ch_repeat(s: str, i: int, c: str) -> int:
    """Count of repeated `c` at `s[i:]`."""

    j = i
    n = len(s)
    while j < n and s[j] == c:
        j += 1
    return j - i


# pulldown-cmark/src/scanners.rs::scan_whitespace_no_nl
def scan_whitespace_no_nl(s: str, i: int) -> int:
    """Count of consecutive ASCII whitespace excluding newlines at `s[i:]`."""

    j = i
    n = len(s)
    while j < n and is_ascii_whitespace_no_nl(s[j]):
        j += 1
    return j - i


# pulldown-cmark/src/scanners.rs::scan_eol
def scan_eol(s: str, i: int) -> int | None:
    """If `s[i:]` starts with a CR / LF / CRLF (or is empty), return the count consumed; else None."""

    n = len(s)
    if i >= n:
        return 0
    c = s[i]
    if c == '\n':
        return 1
    if c == '\r':
        if i + 1 < n and s[i + 1] == '\n':
            return 2
        return 1
    return None


# pulldown-cmark/src/scanners.rs::scan_blank_line
def scan_blank_line(s: str, i: int = 0) -> int | None:
    """
    If `s[i:]` is whitespace-only up to and including an EOL (or end-of-string), return chars consumed up to and
    including the EOL; else None.
    """

    j = i + scan_whitespace_no_nl(s, i)
    eol = scan_eol(s, j)
    if eol is None:
        return None
    return j - i + eol


def is_blank_line(line: str) -> bool:
    """True if `line` (which does not contain a trailing newline) is empty or all-whitespace."""

    if not line:
        return True
    return all(is_ascii_whitespace_no_nl(c) for c in line)
