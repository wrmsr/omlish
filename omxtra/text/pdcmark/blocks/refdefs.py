"""
Reference link definition table + refdef parsing.

Refdefs are collected as paragraphs close. When the paragraph buffer starts with one or more
refdef-shaped sequences of lines, those lines are consumed, the refdef is registered, and only the
remaining lines (if any) emit as paragraph content.

A refdef spans 1, 2, or 3 lines:

  - `[label]: dest "title"`
  - `[label]: dest` / `"title"`
  - `[label]:` / `dest` / `"title"`

(Plus combinations - title is optional; dest and title can each follow the label or sit on their
own line.) See CommonMark §4.7 for the full grammar. Cf. pulldown-cmark/src/firstpass.rs::FirstPass::parse_refdef_total.
"""
import typing as ta

from omlish import dataclasses as dc

from ..scanning.links import normalize_link_label
from ..scanning.links import scan_link_destination
from ..scanning.links import scan_link_label
from ..scanning.links import scan_link_title


##


@dc.dataclass(frozen=True)
class LinkDef:
    dest: str
    title: str


# pulldown-cmark/src/parse.rs::RefDefs - same role (label-keyed table with case-insensitive normalization). We use a
# plain dict; pulldown wraps a HashMap<LinkLabel, LinkDef>.
class RefDefs:
    def __init__(self) -> None:
        super().__init__()

        self._table: dict[str, LinkDef] = {}

    def add(self, label: str, link_def: LinkDef) -> bool:
        """Register a refdef. First wins per CommonMark; returns True if added, False if `label` was already defined."""

        if label in self._table:
            return False
        self._table[label] = link_def
        return True

    def get(self, label: str) -> LinkDef | None:
        return self._table.get(label)

    def __contains__(self, label: str) -> bool:
        return label in self._table

    def __len__(self) -> int:
        return len(self._table)


##


@dc.dataclass(frozen=True)
class RefDefMatch:
    lines_consumed: int
    label: str
    link_def: LinkDef


# pulldown-cmark/src/firstpass.rs::FirstPass::parse_refdef_total - full multi-line version.
def try_consume_refdef(lines: ta.Sequence[str], start: int) -> RefDefMatch | None:
    """
    Try to parse a refdef beginning at `lines[start]`. Returns a RefDefMatch on success, or None if the lines starting
    here are not a valid refdef.

    A refdef may span 1, 2, or 3 lines. The first line must contain `[label]:` (possibly indented up to 3 spaces).
    Destination and title may appear on the same line, the next line, or split across two lines. The refdef must
    terminate at end-of-line (no other content allowed).
    """

    if start >= len(lines):
        return None

    line0 = lines[start]
    n0 = len(line0)
    j = 0
    while j < n0 and line0[j] == ' ' and j < 3:
        j += 1
    if j >= n0 or line0[j] != '[':
        return None
    label_scan = scan_link_label(line0, j)
    if label_scan is None or label_scan.end >= n0 or line0[label_scan.end] != ':':
        return None
    norm = normalize_link_label(label_scan.raw)
    if not norm:
        return None

    # Walk forward from after the colon through up to 2 additional lines, scanning dest then title. We split into
    # "stages": (1) skip whitespace, (2) dest, (3) skip whitespace, (4) optional title. Whitespace skipping may advance
    # through at most one logical newline boundary at a time.
    pos = label_scan.end + 1
    line_ix = start
    line = line0
    nl = n0

    # skip ws before dest
    next_line_ix, next_pos = _skip_ws_across_lines(lines, line_ix, pos, max_newlines=1)
    if next_line_ix is None:
        return None
    line_ix, pos = next_line_ix, next_pos
    line = lines[line_ix]
    nl = len(line)
    if pos >= nl:
        return None

    dest_scan = scan_link_destination(line, pos)
    if dest_scan is None:
        return None
    dest = dest_scan.dest
    pos = dest_scan.end

    # skip ws after dest (may cross newline, allowing title on next line)
    saved_line_ix, saved_pos = line_ix, pos
    nl_line_ix, nl_pos = _skip_ws_across_lines(lines, line_ix, pos, max_newlines=1)

    title = ''
    title_consumed = False

    if nl_line_ix is not None:
        cand_line = lines[nl_line_ix]
        if nl_pos < len(cand_line) and cand_line[nl_pos] in '"\'(':
            title_scan = scan_link_title(cand_line, nl_pos)
            if title_scan is not None:
                # Title valid; the rest of that line must be whitespace.
                tail = cand_line[title_scan.end:]
                if tail.strip() == '':
                    title = title_scan.title
                    line_ix = nl_line_ix
                    pos = title_scan.end
                    title_consumed = True

    if not title_consumed:
        line_ix, pos = saved_line_ix, saved_pos
        # The remainder of dest's line must be whitespace.
        line = lines[line_ix]
        if line[pos:].strip() != '':
            return None

    return RefDefMatch(
        lines_consumed=(line_ix - start) + 1,
        label=norm,
        link_def=LinkDef(dest=dest, title=title),
    )


def _skip_ws_across_lines(
        lines: ta.Sequence[str],
        line_ix: int,
        pos: int,
        *,
        max_newlines: int,
) -> tuple[int | None, int]:
    """
    Consume horizontal whitespace from (line_ix, pos), allowing up to `max_newlines` newline crossings. Returns
    (line_ix, pos) on success, (None, _) on failure (out of bounds).
    """

    newlines = 0
    while True:
        line = lines[line_ix]
        nl = len(line)
        while pos < nl and (line[pos] == ' ' or line[pos] == '\t'):
            pos += 1
        if pos < nl:
            return line_ix, pos
        # End of current line. May cross a newline if budget remains.
        if newlines >= max_newlines:
            return None, 0
        newlines += 1
        line_ix += 1
        pos = 0
        if line_ix >= len(lines):
            return None, 0


# pulldown-cmark/src/firstpass.rs::FirstPass::parse_refdef_total - single-line subset; preserved for the single-line
# code path (still used by the BlockMachine - kept for now to avoid churn, but the multi-line `try_consume_refdef` is
# now the canonical entry point).
def parse_single_line_refdef(line: str) -> tuple[str, LinkDef] | None:
    """
    If `line` is a single-line refdef of shape `[label]: <dest> [title]?`, return the normalized label and a LinkDef.
    Else return None.

    Trailing whitespace on the line is permitted. Anything else after the optional title (or, if no title, after the
    destination) makes the line not a refdef.
    """

    n = len(line)
    j = 0
    while j < n and line[j] == ' ' and j < 3:
        j += 1
    if j >= n or line[j] != '[':
        return None
    label_scan = scan_link_label(line, j)
    if label_scan is None:
        return None
    if label_scan.end >= n or line[label_scan.end] != ':':
        return None
    norm = normalize_link_label(label_scan.raw)
    if not norm:
        return None

    pos = label_scan.end + 1
    while pos < n and (line[pos] == ' ' or line[pos] == '\t'):
        pos += 1
    if pos >= n:
        # Destination on next line - multi-line refdef.
        return None

    dest_scan = scan_link_destination(line, pos)
    if dest_scan is None:
        return None
    pos = dest_scan.end

    while pos < n and (line[pos] == ' ' or line[pos] == '\t'):
        pos += 1

    title = ''
    if pos < n:
        if line[pos] not in '"\'(':
            return None  # garbage after dest
        title_scan = scan_link_title(line, pos)
        if title_scan is None:
            return None
        title = title_scan.title
        pos = title_scan.end
        while pos < n and (line[pos] == ' ' or line[pos] == '\t'):
            pos += 1
        if pos < n:
            return None  # garbage after title

    return norm, LinkDef(dest=dest_scan.dest, title=title)
