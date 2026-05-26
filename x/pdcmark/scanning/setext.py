"""
Setext heading underline scanner.

CommonMark §4.3: an underline of `=` characters (level 1) or `-` characters (level 2), optionally indented up to 3
spaces, optionally followed by trailing spaces / tabs, then EOL. The preceding paragraph (if any) becomes the heading
body.

This module only recognizes the underline. The "promote the previous paragraph to a heading" decision lives in the block
machine.
"""
from .whitespace import is_ascii_whitespace_no_nl
from .whitespace import scan_ch_repeat


##


# pulldown-cmark/src/scanners.rs::scan_setext_heading
def scan_setext_underline(line: str) -> int | None:
    """
    Return heading level (1 or 2) if `line` is a setext underline, else None.

    `line` is the line content without any container markers but with up to 3 spaces of leading indent allowed. Trailing
    whitespace before EOL is permitted.
    """

    i = 0
    n = len(line)
    # Up to 3 leading spaces.
    while i < n and line[i] == ' ' and i < 3:
        i += 1
    if i >= n:
        return None
    c = line[i]
    if c == '=':
        level = 1
    elif c == '-':
        level = 2
    else:
        return None
    underline_chars = scan_ch_repeat(line, i, c)
    if underline_chars < 1:
        return None
    j = i + underline_chars
    # Trailing whitespace only.
    while j < n and is_ascii_whitespace_no_nl(line[j]):
        j += 1
    if j != n:
        return None
    return level
