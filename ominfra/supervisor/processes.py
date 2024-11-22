import abc

from .states import ProcessState


class ProcessStateError(RuntimeError):
    pass


class ProcessStateManager(abc.ABC):
    @abc.abstractmethod
    def change_state(self, new_state: ProcessState, expected: bool = True) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def check_in_state(self, *states: ProcessState) -> None:
        raise NotImplementedError
