# ruff: noqa: SLF001
"""
Start-of-line scanner — indentation, tab expansion, container markers.

Mirrors `pulldown-cmark/src/scanners.rs::LineStart`. The role of this struct is to step through the prefix of a line,
consuming logical "columns" of indentation while respecting CommonMark's tab-stop-of-4 rule. After each container marker
is matched, the same scanner continues consuming relative-to-the-marker indentation, so it stays correct across nested
containers (e.g., `> - foo` consumes `>`, then space, then list marker, then space).

Tab handling. CommonMark treats tabs as advancing to the next multiple of 4 columns from the start of the line. If a
scanner consumes fewer columns than a tab provides, the tab "carries over" as phantom spaces that subsequent scans can
pull from. `tab_carry` tracks those leftover columns.

We diverge from the rust struct in two ways:

  * Working on `str` rather than `&[u8]`; positions are character indices.
  * Public methods are mutating instance methods rather than the rust ports that took `&mut self`. The state being
    mutated is identical.
"""
from .whitespace import is_ascii_whitespace_no_nl
from .whitespace import scan_eol


##


# pulldown-cmark/src/scanners.rs::LineStart — same role, same tab-handling math.
class LineStart:
    __slots__ = ('_line', '_pos', '_tab_origin', '_tab_carry', '_min_hrule')

    def __init__(self, line: str) -> None:
        self._line = line
        self._pos = 0
        # Column of the byte at `_pos` for tab-expansion purposes. Reset after each consumed tab.
        self._tab_origin = 0
        # Leftover phantom-space columns from a tab whose advance was wider than requested.
        self._tab_carry = 0
        # `min_hrule_offset` in pulldown-cmark — caches "no hrule possible before this index".
        self._min_hrule = 0

    @property
    def position(self) -> int:
        return self._pos

    @property
    def line(self) -> str:
        return self._line

    @property
    def tab_carry(self) -> int:
        return self._tab_carry

    def advance(self, n: int) -> None:
        """
        Advance position by `n` characters without re-running scanners. Caller is responsible for keeping tab-origin
        accounting consistent (used for chars guaranteed not to be tabs).
        """

        self._pos += n

    @property
    def min_hrule(self) -> int:
        return self._min_hrule

    @min_hrule.setter
    def min_hrule(self, v: int) -> None:
        self._min_hrule = v

    def clone(self) -> LineStart:
        c = LineStart.__new__(LineStart)
        c._line = self._line
        c._pos = self._pos
        c._tab_origin = self._tab_origin
        c._tab_carry = self._tab_carry
        c._min_hrule = self._min_hrule
        return c

    def restore(self, saved: LineStart) -> None:
        self._pos = saved._pos
        self._tab_origin = saved._tab_origin
        self._tab_carry = saved._tab_carry
        self._min_hrule = saved._min_hrule

    def is_at_eol(self) -> bool:
        if self._pos >= len(self._line):
            return True
        c = self._line[self._pos]
        return c == '\r' or c == '\n'

    def remaining(self) -> str:
        return self._line[self._pos:]

    def remaining_space(self) -> int:
        return self._tab_carry

    def bytes_scanned(self) -> int:
        return self._pos

    # pulldown-cmark/src/scanners.rs::LineStart::scan_space
    def scan_space(self, n_space: int) -> bool:
        """Consume up to `n_space` columns of indentation. True iff all `n_space` were consumed."""

        return self._scan_space_inner(n_space) == 0

    # pulldown-cmark/src/scanners.rs::LineStart::scan_space_upto
    def scan_space_upto(self, n_space: int) -> int:
        """Consume up to `n_space` columns; return the number actually consumed."""

        return n_space - self._scan_space_inner(n_space)

    def _scan_space_inner(self, n_space: int) -> int:
        # First, draw from any leftover tab carry.
        from_carry = min(self._tab_carry, n_space)
        self._tab_carry -= from_carry
        n_space -= from_carry

        line = self._line
        n = len(line)
        while n_space > 0 and self._pos < n:
            c = line[self._pos]
            if c == ' ':
                self._pos += 1
                n_space -= 1
            elif c == '\t':
                advance = 4 - (self._pos - self._tab_origin) % 4
                self._pos += 1
                self._tab_origin = self._pos
                take = min(advance, n_space)
                n_space -= take
                self._tab_carry = advance - take
            else:
                break
        return n_space

    # pulldown-cmark/src/scanners.rs::LineStart::scan_all_space
    def scan_all_space(self) -> None:
        self._tab_carry = 0
        line = self._line
        n = len(line)
        while self._pos < n and is_ascii_whitespace_no_nl(line[self._pos]):
            self._pos += 1

    def scan_ch(self, c: str) -> bool:
        if self._pos < len(self._line) and self._line[self._pos] == c:
            self._pos += 1
            return True
        return False

    def eol_consumed(self) -> int:
        """
        If positioned at an EOL or end-of-string, advance past it (CRLF counts as one) and return the count consumed;
        else 0.
        """

        n = scan_eol(self._line, self._pos)
        if n is None:
            return 0
        self._pos += n
        return n
