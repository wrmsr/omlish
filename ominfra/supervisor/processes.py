import abc
import typing as ta

from .states import ProcessState
from .types import Process


##


class ProcessStateError(RuntimeError):
    pass


class ProcessStateManager(abc.ABC):
    @abc.abstractmethod
    def change_state(self, new_state: ProcessState, expected: bool = True) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def check_in_state(self, *states: ProcessState) -> None:
        raise NotImplementedError


##


class PidHistory(ta.Dict[int, Process]):
    pass
