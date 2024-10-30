import io
import time

from ..term import progress_bar


def test_progress_bar() -> None:
    out = io.StringIO()
    for _ in progress_bar(range(1000), out=out, no_tty_check=True):
        time.sleep(0.0001)
    assert out.getvalue()

    out = io.StringIO()
    for _ in progress_bar(iter(range(1000)), out=out, no_tty_check=True):
        time.sleep(0.0001)
    assert out.getvalue()
