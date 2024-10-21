# ruff: noqa: UP006
import abc
import typing as ta

from .configs import ProcessConfig
from .configs import ServerConfig
from .states import SupervisorState


class AbstractServerContext(abc.ABC):
    @property
    @abc.abstractmethod
    def config(self) -> ServerConfig:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def state(self) -> SupervisorState:
        raise NotImplementedError

    @abc.abstractmethod
    def set_state(self, state: SupervisorState) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def pid_history(self) -> ta.Dict[int, 'AbstractSubprocess']:
        raise NotImplementedError


class AbstractSubprocess(abc.ABC):
    @property
    @abc.abstractmethod
    def pid(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def config(self) -> ProcessConfig:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def context(self) -> AbstractServerContext:
        raise NotImplementedError

    @abc.abstractmethod
    def finish(self, sts: int) -> None:
        raise NotImplementedError
