import time
import typing as ta


TimeoutFn: ta.TypeAlias = ta.Callable[[], float]
Timeout = TimeoutFn | float


class DeadlineTimeout:
    def __init__(
            self,
            deadline: float,
            exc: type[BaseException] | BaseException = TimeoutError,
    ) -> None:
        super().__init__()
        self.deadline = deadline
        self.exc = exc

    def __call__(self) -> float:
        if (rem := self.deadline - time.time()) > 0:
            return rem
        raise self.exc


class InfiniteTimeout:
    def __call__(self) -> float:
        return float('inf')


def timeout_fn(t: Timeout | None) -> TimeoutFn:
    if t is None:
        return InfiniteTimeout()
    if callable(t):
        return t
    if isinstance(t, (float, int)):
        return DeadlineTimeout(time.time() + t)
    raise TypeError(t)
