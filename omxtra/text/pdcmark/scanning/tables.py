"""
GFM pipe-table scanners.

Two scanners:
  - `parse_alignment_row` - recognizes the dashes-and-colons row that confirms a table head. Returns the per-column
    `Alignment` tuple on success.
  - `parse_table_row` - splits a regular row into trimmed cell texts, padded or truncated to the expected column count.

Both handle the GFM rules around leading / trailing pipes, escaped pipes `\\|` inside cells, and optional surrounding
whitespace.

Cf. pulldown-cmark/src/scanners.rs::scan_table_head and pulldown-cmark/src/firstpass.rs::parse_table.
"""
from ..events import Alignment


##


def parse_alignment_row(line: str) -> tuple[Alignment, ...] | None:
    """
    If `line` is a valid GFM table alignment row, return the per-column Alignment tuple. Else return None. The line is
    allowed up to 3 leading spaces of indent and may have an optional leading / trailing `|`. Each cell consists of
    optional `:`, one or more `-`, optional `:`, and surrounding whitespace.
    """

    n = len(line)
    i = 0
    while i < n and line[i] == ' ' and i < 3:
        i += 1
    # Trim trailing whitespace.
    end = n
    while end > i and (line[end - 1] == ' ' or line[end - 1] == '\t'):
        end -= 1
    if i == end:
        return None

    if line[i] == '|':
        i += 1

    if i < end and line[end - 1] == '|':
        end -= 1

    cells: list[Alignment] = []
    while i < end:
        # Skip whitespace.
        while i < end and (line[i] == ' ' or line[i] == '\t'):
            i += 1
        if i >= end:
            return None
        left_colon = False
        right_colon = False
        if line[i] == ':':
            left_colon = True
            i += 1
        # At least one `-`.
        dash_start = i
        while i < end and line[i] == '-':
            i += 1
        if i == dash_start:
            return None
        if i < end and line[i] == ':':
            right_colon = True
            i += 1
        # Skip whitespace.
        while i < end and (line[i] == ' ' or line[i] == '\t'):
            i += 1
        if i < end:
            if line[i] != '|':
                return None
            i += 1
        if left_colon and right_colon:
            cells.append(Alignment.CENTER)
        elif left_colon:
            cells.append(Alignment.LEFT)
        elif right_colon:
            cells.append(Alignment.RIGHT)
        else:
            cells.append(Alignment.NONE)

    if not cells:
        return None
    return tuple(cells)


def parse_table_row(line: str, n_cols: int) -> list[str]:
    """
    Split `line` into `n_cols` cell texts. Extra cells are dropped, missing cells are filled with empty strings.
    Backslash-escaped pipes inside cells are preserved as literal `|` text.
    """

    n = len(line)
    i = 0
    while i < n and line[i] == ' ' and i < 3:
        i += 1
    end = n
    while end > i and (line[end - 1] == ' ' or line[end - 1] == '\t'):
        end -= 1
    if i < end and line[i] == '|':
        i += 1
    if i < end and line[end - 1] == '|':
        # Trailing `|` only if it isn't escaped.
        if not (end >= 2 and line[end - 2] == '\\'):
            end -= 1

    cells: list[str] = []
    cur: list[str] = []
    while i < end:
        c = line[i]
        if c == '\\' and i + 1 < end and line[i + 1] == '|':
            cur.append('|')
            i += 2
            continue
        if c == '|':
            cells.append(''.join(cur).strip())
            cur.clear()
            i += 1
            continue
        cur.append(c)
        i += 1
    cells.append(''.join(cur).strip())

    if len(cells) >= n_cols:
        return cells[:n_cols]
    return cells + [''] * (n_cols - len(cells))


def count_table_cells(line: str) -> int:
    """
    Count the cell positions in `line`, ignoring leading / trailing pipes. Returns 0 if the line contains no pipes (and
    is therefore not a candidate table row).
    """

    n = len(line)
    if n == 0:
        return 0
    i = 0
    while i < n and line[i] == ' ' and i < 3:
        i += 1
    end = n
    while end > i and (line[end - 1] == ' ' or line[end - 1] == '\t'):
        end -= 1
    if i < end and line[i] == '|':
        i += 1
    if i < end and line[end - 1] == '|':
        if not (end >= 2 and line[end - 2] == '\\'):
            end -= 1
    if i >= end:
        return 0
    count = 1
    j = i
    while j < end:
        c = line[j]
        if c == '\\' and j + 1 < end:
            j += 2
            continue
        if c == '|':
            count += 1
        j += 1
    return count


def line_could_be_table_row(line: str) -> bool:
    """
    Cheap heuristic: does the line contain at least one unescaped `|`? Used to decide whether to even attempt the
    alignment-row promotion.
    """

    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == '\\' and i + 1 < n:
            i += 2
            continue
        if c == '|':
            return True
        i += 1
    return False
