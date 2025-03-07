# ruff: noqa: UP006 UP007
# @omlish-lite
import socket
import threading
import typing as ta

from ..lite.timeouts import Timeout
from ..lite.timeouts import TimeoutLike


##


def socket_can_connect(
        address: ta.Any,
        *,
        timeout: ta.Optional[TimeoutLike] = None,
        on_fail: ta.Optional[ta.Callable[[BaseException], None]] = None,
        exception: ta.Union[ta.Type[BaseException], ta.Tuple[ta.Type[BaseException], ...]] = (ConnectionRefusedError,),
) -> bool:
    timeout = Timeout.of(timeout)

    try:
        conn = socket.create_connection(address, timeout=timeout.or_(None))

    except exception as e:  # noqa
        if on_fail is not None:
            on_fail(e)
        return False

    else:
        conn.close()
        return True


def socket_wait_until_can_connect(
        address: ta.Any,
        *,
        timeout: ta.Optional[TimeoutLike] = None,
        on_fail: ta.Optional[ta.Callable[[BaseException], None]] = None,
        sleep_s: float = .1,
        exception: ta.Union[ta.Type[BaseException], ta.Tuple[ta.Type[BaseException], ...]] = (ConnectionRefusedError,),
        cancel_event: ta.Optional[threading.Event] = None,
) -> None:
    timeout = Timeout.of(timeout)

    if cancel_event is None:
        cancel_event = threading.Event()

    while not cancel_event.is_set():
        timeout()

        if socket_can_connect(
            address,
            timeout=timeout,
            on_fail=on_fail,
            exception=exception,
        ):
            break

        cancel_event.wait(min(sleep_s, timeout.remaining()))
