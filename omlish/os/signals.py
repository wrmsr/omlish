# ruff: noqa: UP006 UP007
# @omlish-lite
import signal


def parse_signal(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        pass

    s = s.upper()
    if not s.startswith('SIG'):
        s = 'SIG' + s
    return signal.Signals[s]  # noqa
