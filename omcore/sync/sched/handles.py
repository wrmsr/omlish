import threading
import time
import typing as ta

from .types import ScheduledCallback
from .types import ScheduledCancelledError
from .types import ScheduledTimeoutError
from .types import ScheduleHandle


##


class ScheduleHandleImpl(ScheduleHandle):
    """
    A cancellable handle for a scheduled function.

    Thread-safe. Callbacks run in the runner thread (so keep them short).
    """

    def __init__(self, cv: threading.Condition) -> None:
        super().__init__()

        self._cv = cv
        self._callbacks: list[ScheduledCallback] = []

    _done = False
    _cancelled = False
    _running = False
    _result: ta.Any = None
    _exc: BaseException | None = None

    # status

    def done(self) -> bool:
        with self._cv:
            return self._done

    def cancelled(self) -> bool:
        with self._cv:
            return self._cancelled

    def running(self) -> bool:
        with self._cv:
            return self._running

    # callbacks

    def _invoke_callbacks(self, cbs: ta.Sequence[ScheduledCallback]) -> None:
        for cb in cbs:
            cb(self)

    # completion

    def cancel(self) -> bool:
        with self._cv:
            if self._done or self._running:
                return False
            if self._cancelled:
                return True

            self._cancelled = True
            self._done = True

            cbs = list(self._callbacks)
            self._callbacks.clear()

            self._cv.notify_all()

        # Callbacks run outside lock (in caller thread)
        self._invoke_callbacks(cbs)

        return True

    def result(self, timeout: float | None = None) -> ta.Any:
        with self._cv:
            if not self._wait_done_locked(timeout):
                raise ScheduledTimeoutError('scheduled result timed out')
            if self._cancelled:
                raise ScheduledCancelledError('scheduled task was cancelled')

            if self._exc is not None:
                raise self._exc
            return self._result

    def exception(self, timeout: float | None = None) -> BaseException | None:
        with self._cv:
            if not self._wait_done_locked(timeout):
                raise ScheduledTimeoutError('scheduled result timed out')
            if self._cancelled:
                raise ScheduledCancelledError('scheduled task was cancelled')

            return self._exc

    def add_done_callback(self, fn: ScheduledCallback) -> None:
        call_now = False

        with self._cv:
            if self._done:
                call_now = True
            else:
                self._callbacks.append(fn)

        if call_now:
            fn(self)

    # internal (runner thread)

    def _set_running(self) -> None:
        with self._cv:
            self._running = True

    def _set_result(self, result: ta.Any) -> None:
        with self._cv:
            if self._done:
                return

            self._result = result
            self._exc = None
            self._running = False
            self._done = True

            cbs = list(self._callbacks)
            self._callbacks.clear()

            self._cv.notify_all()

        self._invoke_callbacks(cbs)

    def _set_exception(self, exc: BaseException) -> None:
        with self._cv:
            if self._done:
                return

            self._result = None
            self._exc = exc
            self._running = False
            self._done = True

            cbs = list(self._callbacks)
            self._callbacks.clear()

            self._cv.notify_all()

        self._invoke_callbacks(cbs)

    def _wait_done_locked(self, timeout: float | None) -> bool:
        if self._done:
            return True

        if timeout is None:
            while not self._done:
                self._cv.wait()
            return True  # type: ignore[unreachable]  # ??

        deadline = time.monotonic() + max(0.0, float(timeout))
        while not self._done:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            self._cv.wait(timeout=remaining)

        return True  # type: ignore[unreachable]  # ??
