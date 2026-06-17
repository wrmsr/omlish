import threading
import typing as ta


##


class HasLock:
    def __init__(
            self,
            *,
            lock: threading.RLock | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__()

        self._lock = lock if lock is not None else threading.RLock()
