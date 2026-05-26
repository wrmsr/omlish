"""
Blockquote marker scanner.

CommonMark §5.1: a blockquote starts with `>` (optionally indented up to 3 spaces) followed optionally by a single space
(or tab) before the content.
"""


##


# pulldown-cmark/src/scanners.rs::scan_blockquote_start — same semantics; we don't take leading indent (the BlockMachine
# consumes that via LineStart before calling us).
def scan_blockquote_marker(line: str, i: int = 0) -> int | None:
    """
    If `line[i]` is `>`, return chars consumed (1 if no following space, 2 if a space / tab follows), else None.
    Position is assumed already past any allowed leading indent.
    """

    n = len(line)
    if i >= n or line[i] != '>':
        return None
    j = i + 1
    if j < n and (line[j] == ' ' or line[j] == '\t'):
        return j + 1 - i
    return 1
