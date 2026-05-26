"""
Thematic break (HR) scanner.

CommonMark §4.1: a line consisting of three or more matching `-`, `_`, or `*` characters, optionally separated by spaces
or tabs, optionally indented up to 3 spaces, possibly followed by trailing spaces / tabs, then EOL.
"""


##


# pulldown-cmark/src/scanners.rs::scan_hrule - same semantics; we return a plain bool instead of Rust's Result<usize,
# usize>. The position-bound caching that motivates the Err(min_offset) form in Rust is handled separately by
# LineStart.min_hrule on our side.
def scan_hrule(line: str) -> bool:
    i = 0
    n = len(line)
    # Up to 3 leading spaces.
    while i < n and line[i] == ' ' and i < 3:
        i += 1
    if i >= n:
        return False
    c = line[i]
    if c not in '-_*':
        return False
    count = 0
    while i < n:
        ch = line[i]
        if ch == c:
            count += 1
        elif ch == ' ' or ch == '\t':
            pass
        else:
            return False
        i += 1
    return count >= 3
