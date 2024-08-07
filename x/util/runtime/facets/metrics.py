import abc
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class Metric:
    name: str
    value: ta.Optional[float] = None


class Metrics(abc.ABC):
    @abc.abstractmethod
    def send(self, metric: Metric) -> None:
        raise NotImplementedError
