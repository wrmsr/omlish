# ruff: noqa: UP006 UP007
import abc
import time
import typing as ta


TimeoutLike = ta.Union['Timeout', float]  # ta.TypeAlias


##


class Timeout(abc.ABC):
    @abc.abstractmethod
    def __call__(self) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    def or_(self, o: ta.Any) -> ta.Any:
        raise NotImplementedError

    @classmethod
    def of(cls, t: ta.Optional[TimeoutLike]) -> 'Timeout':
        if t is None:
            return InfiniteTimeout()

        elif isinstance(t, Timeout):
            return t

        elif isinstance(t, (float, int)):
            return DeadlineTimeout(time.time() + t)

        else:
            raise TypeError(t)


class DeadlineTimeout(Timeout):
    def __init__(
            self,
            deadline: float,
            exc: ta.Union[ta.Type[BaseException], BaseException] = TimeoutError,
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
