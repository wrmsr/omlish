import functools
import time
import typing as ta


TimeoutFn: ta.TypeAlias = ta.Callable[[], float]
Timeout = TimeoutFn | float


class TimeoutTicker:
    def __init__(
            self,
            deadline: float,
            exc: type[BaseException] | BaseException = TimeoutError,
    ) -> None:
        super().__init__()
        self.deadline = deadline
        self.exc = exc

    def __call__(self) -> float:
        if (rem := time.time() - self.deadline) > 0:
            return rem
        raise self.exc


def timeout_fn(t: Timeout | None) -> TimeoutFn:
    raise NotImplementedError


