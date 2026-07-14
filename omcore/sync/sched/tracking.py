import threading

from .types import ScheduledFn
from .types import ScheduledRunner
from .types import ScheduledRunnerState
from .types import ScheduleHandle


##


class TrackingScheduledRunner(ScheduledRunner):
    def __init__(self, inner: ScheduledRunner) -> None:
        super().__init__()

        self._inner = inner

        self._lock = threading.Lock()
        self._handles: set[ScheduleHandle] = set()

    def get_state(self) -> ScheduledRunnerState:
        return self._inner.get_state()

    def get_handles(self) -> set[ScheduleHandle]:
        with self._lock:
            return set(self._handles)

    def cancel_all_handles(self) -> None:
        with self._lock:
            hs = list(self._handles)

        for h in hs:
            h.cancel()

    def _track_handle(self, h: ScheduleHandle) -> ScheduleHandle:
        with self._lock:
            self._handles.add(h)

        def _done(_h: ScheduleHandle) -> None:
            with self._lock:
                self._handles.discard(_h)

        h.add_done_callback(_done)
        return h

    #

    def schedule(self, delay: float, fn: ScheduledFn) -> ScheduleHandle:
        return self._track_handle(self._inner.schedule(delay, fn))

    def shutdown(
            self,
            *,
            cancel_all: bool = False,
            no_wait: bool = False,
            timeout: float | None = None,
    ) -> None:
        self._inner.shutdown(
            cancel_all=cancel_all,
            no_wait=no_wait,
            timeout=timeout,
        )

    def wait(self, timeout: float | None = None) -> None:
        self._inner.wait(timeout=timeout)
