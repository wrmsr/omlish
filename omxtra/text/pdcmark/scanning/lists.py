"""
List marker scanners - bullet, ordered, and task-list-item-marker.

CommonMark §5.2. Bullet markers are `-`, `+`, or `*`. Ordered markers are 1-9 decimal digits followed by `.` or `)`. The
marker must be followed by either a space / tab or end-of-line (otherwise the line is plain text).

We return only the marker descriptor itself. Post-marker indent / tab handling lives in the BlockMachine (it needs
`LineStart` for correct tab-stop accounting).
"""
from omcore import dataclasses as dc


##


# pulldown-cmark/src/scanners.rs::LineStart::scan_list_marker_with_indent and scan_listitem - split here into a pure
# marker-only scanner; the indent calculation lives in the BlockMachine.

# CommonMark spec caps ordered-list start numbers at 9 digits.
_MAX_ORDERED_DIGITS = 9


@dc.dataclass(frozen=True)
class ListMarker:
    char: str           # '-', '+', '*', '.', or ')'
    is_ordered: bool
    start: int         # 0 for unordered; the parsed number for ordered
    marker_width: int  # chars consumed by the marker itself (1 for bullets, 2..10 for ordered)


def scan_list_marker(line: str, i: int = 0) -> ListMarker | None:
    n = len(line)
    if i >= n:
        return None
    c = line[i]

    if c in '-+*':
        # The marker must be followed by space, tab, or EOL.
        if i + 1 < n:
            nxt = line[i + 1]
            if nxt != ' ' and nxt != '\t':
                return None
        return ListMarker(char=c, is_ordered=False, start=0, marker_width=1)

    if c.isdigit():
        j = i
        digits = 0
        while j < n and line[j].isdigit():
            digits += 1
            if digits > _MAX_ORDERED_DIGITS:
                return None
            j += 1
        if j >= n:
            return None
        delim = line[j]
        if delim != '.' and delim != ')':
            return None
        # Same trailing-space-or-EOL rule.
        if j + 1 < n:
            nxt = line[j + 1]
            if nxt != ' ' and nxt != '\t':
                return None
        try:
            start = int(line[i:j])
        except ValueError:
            return None
        return ListMarker(char=delim, is_ordered=True, start=start, marker_width=j - i + 1)

    return None


@dc.dataclass(frozen=True)
class TaskListMark:
    checked: bool
    end: int   # one past the closing `]`


# pulldown-cmark/src/scanners.rs::LineStart::scan_task_list_marker
def scan_task_list_marker(line: str, i: int = 0) -> TaskListMark | None:
    """
    Recognize `[ ]`, `[x]`, or `[X]` followed by whitespace.

    Position `i` should be just past the list-item marker and its trailing whitespace.
    """

    n = len(line)
    # Allow up to 3 leading spaces between the list marker and the task box, like pulldown.
    j = i
    spaces = 0
    while j < n and line[j] == ' ' and spaces < 3:
        j += 1
        spaces += 1
    if j >= n or line[j] != '[':
        return None
    j += 1
    if j >= n:
        return None
    box = line[j]
    if box == ' ' or box == '\t':
        checked = False
    elif box == 'x' or box == 'X':
        checked = True
    else:
        return None
    j += 1
    if j >= n or line[j] != ']':
        return None
    j += 1
    # The closing `]` must be followed by whitespace.
    if j < n and line[j] != ' ' and line[j] != '\t':
        return None
    return TaskListMark(checked=checked, end=j)
