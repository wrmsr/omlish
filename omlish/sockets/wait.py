# ruff: noqa: UP006 UP007
# @omlish-lite
import socket
import threading
import typing as ta

from ..lite.timeouts import Timeout
from ..lite.timeouts import TimeoutLike


def socket_wait_until_can_connect(
        address: ta.Any,
        *,
        timeout: ta.Optional[TimeoutLike] = None,
        on_fail: ta.Optional[ta.Callable[[BaseException], None]] = None,
        sleep_s: float = .1,
        exception: ta.Union[ta.Type[BaseException], ta.Tuple[ta.Type[BaseException], ...]] = (Exception,),
        cancel_event: ta.Optional[threading.Event] = None,
) -> None:
    timeout = Timeout.of(timeout)

    if cancel_event is None:
        cancel_event = threading.Event()

    while not cancel_event.is_set():
        timeout()

        try:
            conn = socket.create_connection(address, timeout=timeout.or_(None))

        except exception as e:  # noqa
            if on_fail is not None:
                on_fail(e)

        else:
            conn.close()
            break

        cancel_event.wait(min(sleep_s, timeout.remaining()))
