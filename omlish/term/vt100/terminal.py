import dataclasses as dc
import string
import typing as ta

from ...lite.check import check


T = ta.TypeVar('T')


##


@dc.dataclass()
class Cell:
    """Represents a single character cell in the terminal with attributes."""

    char: str = ' '

    fg: str = 'default'
    bg: str = 'default'

    bold: bool = False
    underline: bool = False
    reverse: bool = False

    def __repr__(self):
        return f'Cell({self.char!r}, bold={self.bold}, underline={self.underline})'


class Vt100Terminal:
    def __init__(
            self,
            rows: int = 24,
            cols: int = 80,
    ) -> None:
        super().__init__()

        self._rows = rows
        self._cols = cols

        # 2D array of Cell objects
        self._screen = [
            [Cell() for _ in range(cols)]
            for _ in range(rows)
        ]

        # Current cursor position (row, col), 0-based internally
        self._cursor_row = 0
        self._cursor_col = 0

        # Current text attributes
        self._current_fg = 'default'
        self._current_bg = 'default'
        self._current_bold = False
        self._current_underline = False
        self._current_reverse = False

        # Parser state
        self._state: ta.Literal['normal', 'esc', 'csi'] = 'normal'
        self._escape_buffer: list[str] = []

    def parse_byte(self, byte: int | str) -> None:
        """Parse a single byte of input (as an integer or a single-character string)."""

        if isinstance(byte, int):
            byte = chr(byte)

        if self._state == 'normal':
            if byte == '\x1b':
                # Start of escape sequence
                self._state = 'esc'
                self._escape_buffer = [byte]
            elif byte == '\r':
                # Carriage return
                self._cursor_col = 0
            elif byte == '\n':
                # Line feed
                self._cursor_row = min(self._cursor_row + 1, self._rows - 1)
            elif byte == '\b':
                # Backspace
                self._cursor_col = max(self._cursor_col - 1, 0)
            elif byte in string.printable and byte not in ['\x0b', '\x0c']:
                # Printable ASCII (excluding form feeds, vertical tabs, etc.)
                self._put_char(byte)
            else:
                # Ignore other control characters
                pass

        elif self._state == 'esc':
            self._escape_buffer.append(byte)
            if byte == '[':
                # Move to CSI state (Control Sequence Introducer)
                self._state = 'csi'
            # Some escape codes like ESCc, ESC7, etc. are possible but we'll ignore or handle them in a minimal way. If
            # no further instructions, revert to normal
            elif len(self._escape_buffer) == 2:
                # We only support ESC + [ in this example, so revert
                self._state = 'normal'

        elif self._state == 'csi':
            self._escape_buffer.append(byte)
            # Check if this byte ends the sequence (typical final bytes are A-Z, @, etc.)
            if byte.isalpha() or byte in '@`~':
                # We have a complete CSI sequence: parse it
                self._parse_csi(''.join(self._escape_buffer))
                # Reset state
                self._state = 'normal'
                self._escape_buffer = []

    def _put_char(self, ch: str) -> None:
        """Write a character at the current cursor position, and advance the cursor."""

        if 0 <= self._cursor_row < self._rows and 0 <= self._cursor_col < self._cols:
            cell = self._screen[self._cursor_row][self._cursor_col]
            cell.char = ch
            cell.fg = self._current_fg
            cell.bg = self._current_bg
            cell.bold = self._current_bold
            cell.underline = self._current_underline
            cell.reverse = self._current_reverse

        self._cursor_col += 1
        if self._cursor_col >= self._cols:
            self._cursor_col = 0
            self._cursor_row = min(self._cursor_row + 1, self._rows - 1)

    def _parse_csi(self, seq: str) -> None:
        """
        Parse a CSI (Control Sequence Introducer) escape sequence. Typically looks like: ESC [ parameters letter For
        example: ESC [ 2 J, ESC [ 10 ; 20 H, etc.
        """

        # seq includes the initial ESC[. e.g. "\x1b[10;20H"
        # We'll strip ESC[ and parse what remains.
        check.state(seq.startswith('\x1b['))
        body = seq[2:]  # everything after ESC[

        # Find final character that determines the command (e.g. 'A', 'B', 'H', 'J', 'K', 'm', etc.)
        final = body[-1]
        params = body[:-1]

        # Split params by semicolons, handle empty as '0'
        if params.strip() == '':
            numbers = [0]
        else:
            numbers = [int(x) if x.isdigit() else 0 for x in params.split(';')]

        if final in 'ABCD':
            # Cursor movement
            n = numbers[0] if numbers else 1
            if final == 'A':
                # Up
                self._cursor_row = max(self._cursor_row - n, 0)
            elif final == 'B':
                # Down
                self._cursor_row = min(self._cursor_row + n, self._rows - 1)
            elif final == 'C':
                # Right
                self._cursor_col = min(self._cursor_col + n, self._cols - 1)
            elif final == 'D':
                # Left
                self._cursor_col = max(self._cursor_col - n, 0)

        elif final in 'Hf':
            # Cursor position
            # CSI row;colH or CSI row;colf (1-based coords)
            row = numbers[0] if len(numbers) > 0 else 1
            col = numbers[1] if len(numbers) > 1 else 1
            self._cursor_row = min(max(row - 1, 0), self._rows - 1)
            self._cursor_col = min(max(col - 1, 0), self._cols - 1)

        elif final == 'J':
            # Erase display
            # n=0 -> clear from cursor down,
            # n=1 -> clear from cursor up,
            # n=2 -> clear entire screen
            n = numbers[0] if numbers else 0
            if n == 2:
                self._clear_screen()
            elif n == 0:
                self._clear_down()
            elif n == 1:
                self._clear_up()
            # else: unsupported J mode, ignore

        elif final == 'K':
            # Erase line
            # n=0 -> clear from cursor right
            # n=1 -> clear from cursor left
            # n=2 -> clear entire line
            n = numbers[0] if numbers else 0
            if n == 2:
                self._clear_line(self._cursor_row)
            elif n == 0:
                self._clear_right(self._cursor_row, self._cursor_col)
            elif n == 1:
                self._clear_left(self._cursor_row, self._cursor_col)
            # else: ignore

        elif final == 'm':
            # SGR - Select Graphic Rendition
            # We handle a subset: 0 (reset), 1 (bold), 4 (underline), 7 (reverse)
            # Colors could be extended, but here we keep it minimal
            for code in numbers:
                if code == 0:
                    self._current_fg = 'default'
                    self._current_bg = 'default'
                    self._current_bold = False
                    self._current_underline = False
                    self._current_reverse = False
                elif code == 1:
                    self._current_bold = True
                elif code == 4:
                    self._current_underline = True
                elif code == 7:
                    self._current_reverse = True
                # You can add more codes for color, etc.
                else:
                    # Unsupported SGR code - ignore gracefully
                    pass

        else:
            # Unsupported final - ignore gracefully
            pass

    # hods for Erase Operations

    def _clear_screen(self) -> None:
        for r in range(self._rows):
            for c in range(self._cols):
                self._screen[r][c] = Cell()

    def _clear_down(self) -> None:
        """Clear from cursor to the end of the screen."""

        # Clear current line from cursor forward
        self._clear_right(self._cursor_row, self._cursor_col)

        # Clear all lines below cursor
        for r in range(self._cursor_row + 1, self._rows):
            self._clear_line(r)

    def _clear_up(self) -> None:
        """Clear from the start of the screen up to the cursor."""

        # Clear current line from start to cursor
        self._clear_left(self._cursor_row, self._cursor_col)

        # Clear all lines above cursor
        for r in range(self._cursor_row):
            self._clear_line(r)

    def _clear_line(self, row: int) -> None:
        for c in range(self._cols):
            self._screen[row][c] = Cell()

    def _clear_right(self, row: int, col: int) -> None:
        for c in range(col, self._cols):
            self._screen[row][c] = Cell()

    def _clear_left(self, row: int, col: int) -> None:
        for c in range(col + 1):
            self._screen[row][c] = Cell()

    # Debug/Utility Methods

    def get_screen_as_strings(self) -> list[str]:
        """Return a list of strings representing each row (ignoring attributes). Useful for debugging/testing."""

        return [''.join(cell.char for cell in row) for row in self._screen]
