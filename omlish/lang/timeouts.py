import abc
import time
import typing as ta


TimeoutLike: ta.TypeAlias = ta.Union['Timeout', float]


class Timeout(abc.ABC):
    @abc.abstractmethod
    def __call__(self) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    def or_(self, o: ta.Any) -> ta.Any:
        raise NotImplementedError


class DeadlineTimeout(Timeout):
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

    def or_(self, o: ta.Any) -> ta.Any:
        return self()


class InfiniteTimeout(Timeout):
    def __call__(self) -> float:
        return float('inf')

    def or_(self, o: ta.Any) -> ta.Any:
        return o


def timeout(t: TimeoutLike | None) -> Timeout:
    if t is None:
        return InfiniteTimeout()
    if isinstance(t, Timeout):
        return t
    if isinstance(t, (float, int)):
        return DeadlineTimeout(time.time() + t)
    raise TypeError(t)
