import io


##


_ESC = '\x1b'


def _csi(seq: str) -> str:
    return f'{_ESC}[{seq}'


_RESET = _csi('0m')
_ENTER_ALT = _csi('?1049h')
_LEAVE_ALT = _csi('?1049l')
_HIDE_CURSOR = _csi('?25l')
_SHOW_CURSOR = _csi('?25h')
_CLEAR_LINE = _csi('2K')

_SYNC_OUTPUT_ON = _csi('?2026h')
_SYNC_OUTPUT_OFF = _csi('?2026l')


def _move(row: int, col: int) -> str:
    return _csi(f'{row};{col}H')  # CUP


_MOVE_BOTTOM_LEFT = _move(999, 1)  # clamped


##


def render_write_from_alt(
        *chunks: str,
        no_sync_output: bool = False,
        move_and_clear: bool = False,
        no_reset: bool = False,
) -> str:
    out = io.StringIO()

    if not no_sync_output:
        out.write(_SYNC_OUTPUT_ON)

    if not no_reset:
        # Leave the alt screen in a clean rendition state.
        out.write(_RESET)

    out.write(_HIDE_CURSOR)
    out.write(_LEAVE_ALT)

    if not no_reset:
        # Also start writing to the normal screen from a clean rendition state.
        out.write(_RESET)

    if move_and_clear:
        out.write(_MOVE_BOTTOM_LEFT)
        out.write(_CLEAR_LINE)

    for chunk in chunks:
        out.write(chunk)

    if not no_reset:
        # End the normal-screen write cleanly too.
        out.write(_RESET)

    # Re-enter alt screen cleanly.
    out.write(_ENTER_ALT)
    if not no_reset:
        out.write(_RESET)
    out.write(_SHOW_CURSOR)

    if not no_sync_output:
        out.write(_SYNC_OUTPUT_OFF)

    return out.getvalue()
