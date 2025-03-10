# ruff: noqa: UP006 UP007
# @omlish-lite
import signal
import typing as ta


def parse_signal(s: ta.Union[int, str]) -> int:
    if isinstance(s, int):
        return s

    try:
        return int(s)
    except ValueError:
        pass

    s = s.upper()
    if not s.startswith('SIG'):
        s = 'SIG' + s
    return signal.Signals[s]  # noqa
