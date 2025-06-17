# @omlish-lite
# ruff: noqa: UP006 UP007 UP045
import threading
import time
import typing as ta

from ...lite.check import check
from ..addresses import SocketAndAddress
from .handlers import SocketServerHandler


##


class ThreadingSocketServerHandler:
    def __init__(
            self,
            handler: SocketServerHandler,
            *,
            shutdown_timeout: ta.Optional[float] = None,
    ) -> None:
        super().__init__()

        self._handler = handler
        self._shutdown_timeout = shutdown_timeout

        self._lock = threading.RLock()
        self._threads: ta.List[threading.Thread] = []
        self._is_shutdown = False

    @property
    def handler(self) -> SocketServerHandler:
        return self._handler

    #

    def __call__(self, conn: SocketAndAddress) -> None:
        self.handle(conn)

    def handle(self, conn: SocketAndAddress) -> None:
        with self._lock:
            check.state(not self._is_shutdown)

            self._reap()

            t = threading.Thread(
                target=self._handler,
                args=(conn,),
            )

            self._threads.append(t)

            t.start()

    #

    def _reap(self) -> None:
        with self._lock:
            self._threads[:] = (thread for thread in self._threads if thread.is_alive())

    def is_alive(self) -> bool:
        with self._lock:
            self._reap()

            return bool(self._threads)

    def join(self, timeout: ta.Optional[float] = None) -> None:
        if timeout is not None:
            deadline: ta.Optional[float] = time.time() + timeout
        else:
            deadline = None

        def calc_timeout() -> ta.Optional[float]:
            if deadline is None:
                return None

            tt = deadline - time.time()
            if tt <= 0:
                raise TimeoutError

            return tt

        if not (self._lock.acquire(timeout=calc_timeout() or -1)):
            raise TimeoutError

        try:
            self._reap()

            for t in self._threads:
                t.join(timeout=calc_timeout())

                if t.is_alive():
                    raise TimeoutError

        finally:
            self._lock.release()

    #

    class _NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def shutdown(
            self,
            block: bool = False,
            timeout: ta.Union[float, None, ta.Type[_NOT_SET]] = _NOT_SET,
    ) -> None:
        self._is_shutdown = True

        if block:
            if timeout is self._NOT_SET:
                timeout = self._shutdown_timeout

            self.join(timeout=timeout)  # type: ignore

    #

    def __enter__(self) -> 'ThreadingSocketServerHandler':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
