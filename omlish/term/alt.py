import io


##


_ESC = '\x1b'


def _csi(seq: str) -> str:
    return f'{_ESC}[{seq}'


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
        s: str,
        *,
        no_sync_output: bool = False,
        move_and_clear: bool = False,
) -> str:
    out = io.StringIO()

    if not no_sync_output:
        out.write(_SYNC_OUTPUT_ON)

    out.write(_HIDE_CURSOR)
    out.write(_LEAVE_ALT)

    if move_and_clear:
        out.write(_MOVE_BOTTOM_LEFT)
        out.write(_CLEAR_LINE)

    out.write(s)

    out.write(_ENTER_ALT)
    out.write(_SHOW_CURSOR)

    if not no_sync_output:
        out.write(_SYNC_OUTPUT_OFF)

    return out.getvalue()
