"""
ATX heading scanner.

CommonMark §4.2: opening sequence of 1-6 `#` characters, followed by a space, a tab, or end-of-line. The line content
runs until end-of-line; optional trailing `#` sequence (preceded by space and followed by spaces only) is stripped.

This module provides the scan side; trimming the trailing `#` run lives in `strip_atx_trailers` for the block machine to
call after isolating the content.
"""
from omcore import dataclasses as dc

from .whitespace import scan_ch_repeat


##


@dc.dataclass(frozen=True)
class AtxOpen:
    level: int          # 1..6
    content_start: int  # offset in the input line where heading content begins
    content_end: int    # one past the end of the content (after stripping trailing-hash run)


# pulldown-cmark/src/scanners.rs::scan_atx_heading - returns just the level. We also compute the content slice in the
# same pass because the block machine wants both anyway.
def scan_atx_open(line: str, i: int = 0) -> AtxOpen | None:
    level = scan_ch_repeat(line, i, '#')
    if level == 0 or level > 6:
        return None

    after_hashes = i + level
    n = len(line)

    if after_hashes < n:
        c = line[after_hashes]
        if c != ' ' and c != '\t':
            return None
    # else: heading content is empty (e.g. `# ` then EOL, or just `#` then EOL).

    # Skip spaces / tabs separating opening hashes from content.
    content_start = after_hashes
    while content_start < n and (line[content_start] == ' ' or line[content_start] == '\t'):
        content_start += 1

    # Trim trailing whitespace + a possible closing-hash run preceded by whitespace.
    end = n
    while end > content_start and (line[end - 1] == ' ' or line[end - 1] == '\t'):
        end -= 1

    # If end of content has a `#` run preceded by a space (or is at the start), strip it.
    hash_end = end
    while hash_end > content_start and line[hash_end - 1] == '#':
        hash_end -= 1
    if hash_end < end:
        # We did strip some `#`s. Only valid if preceded by whitespace or content_start.
        if hash_end == content_start or line[hash_end - 1] == ' ' or line[hash_end - 1] == '\t':
            end = hash_end
            while end > content_start and (line[end - 1] == ' ' or line[end - 1] == '\t'):
                end -= 1

    return AtxOpen(level=level, content_start=content_start, content_end=end)
