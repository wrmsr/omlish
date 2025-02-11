# ruff: noqa: UP006 UP007
import abc
import time
import typing as ta


TimeoutLike = ta.Union['Timeout', 'Timeout.Default', float]  # ta.TypeAlias


##


class Timeout(abc.ABC):
    @abc.abstractmethod
    def __call__(self) -> float:
        """Returns the time (in seconds) remaining until the timeout expires, or raises if the timeout has expired."""

        raise NotImplementedError

    @abc.abstractmethod
    def or_(self, o: ta.Any) -> ta.Any:
        """Evaluates time remaining via __call__ if this is a meaningfully configured timeout, otherwise returns `o`."""

        raise NotImplementedError

    #

    @classmethod
    def _now(cls) -> float:
        return time.time()

    #

    class Default:
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    class _NOT_SPECIFIED:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    @classmethod
    def of(
            cls,
            obj: ta.Optional[TimeoutLike],
            default: ta.Union[TimeoutLike, ta.Type[_NOT_SPECIFIED]] = _NOT_SPECIFIED,
    ) -> 'Timeout':
        if obj is None:
            return InfiniteTimeout()

        elif isinstance(obj, Timeout):
            return obj

        elif isinstance(obj, (float, int)):
            return DeadlineTimeout(cls._now() + obj)

        elif obj is Timeout.Default:
            if default is Timeout._NOT_SPECIFIED or default is Timeout.Default:
                raise RuntimeError('Must specify a default timeout')

            else:
                return Timeout.of(default)  # type: ignore[arg-type]

        else:
            raise TypeError(obj)


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
        if (rem := self.deadline - self._now()) > 0:
            return rem
        raise self.exc

    def or_(self, o: ta.Any) -> ta.Any:
        return self()


class InfiniteTimeout(Timeout):
    def __call__(self) -> float:
        return float('inf')

    def or_(self, o: ta.Any) -> ta.Any:
        return o
