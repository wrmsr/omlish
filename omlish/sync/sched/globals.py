import threading

from .heapq import HeapqScheduledRunner  # noqa
from .hwt import HwtScheduledRunner  # noqa
from .types import ScheduledRunner


##


_GLOBAL_SCHEDULED_RUNNER_CLS: type[ScheduledRunner] = (
    HeapqScheduledRunner
    # HwtScheduledRunner
)


# Global singleton (simple for now)
_GLOBAL_LOCK = threading.Lock()
_GLOBAL_SCHEDULED_RUNNER: ScheduledRunner | None = None


def get_scheduled_runner() -> ScheduledRunner:
    global _GLOBAL_SCHEDULED_RUNNER
    with _GLOBAL_LOCK:
        if _GLOBAL_SCHEDULED_RUNNER is None:
            _GLOBAL_SCHEDULED_RUNNER = _GLOBAL_SCHEDULED_RUNNER_CLS()
        return _GLOBAL_SCHEDULED_RUNNER
