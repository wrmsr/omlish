import abc
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class Error:
    exc: ta.Optional[BaseException] = None


class Errors(abc.ABC):
    @abc.abstractmethod
    def report(self, error: Error) -> None:
        raise NotImplementedError
