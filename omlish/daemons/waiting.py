import abc
import functools
import socket
import typing as ta

from .. import dataclasses as dc


##


class Wait(dc.Case):
    pass


class Waiter(abc.ABC):
    @abc.abstractmethod
    def do_wait(self) -> bool:
        raise NotImplementedError


@functools.singledispatch
def waiter_for(wait: Wait) -> Waiter:
    raise TypeError(wait)


##


class SequentialWait(Wait):
    waits: ta.Sequence[Wait]


class SequentialWaiter(Waiter):
    def __init__(self, waiters: ta.Sequence[Waiter]) -> None:
        super().__init__()

        self._waiters = waiters
        self._idx = 0

    def do_wait(self) -> bool:
        while self._idx < len(self._waiters):
            if not self._waiters[self._idx].do_wait():
                return False
            self._idx += 1
        return True


@waiter_for.register
def _(wait: SequentialWait) -> SequentialWaiter:
    return SequentialWaiter([waiter_for(c) for c in wait.waits])


##


class FnWait(Wait):
    fn: ta.Callable[[], bool]


class FnWaiter(Waiter, dc.Frozen):
    wait: FnWait

    def do_wait(self) -> bool:
        return self.wait.fn()


@waiter_for.register
def _(wait: FnWait) -> FnWaiter:
    return FnWaiter(wait)


##


class ConnectWait(Wait):
    address: ta.Any


class ConnectWaiter(Waiter, dc.Frozen):
    wait: ConnectWait

    def do_wait(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(self.wait.address)
            except ConnectionRefusedError:
                return False
            else:
                return True


@waiter_for.register
def _(wait: ConnectWait) -> ConnectWaiter:
    return ConnectWaiter(wait)
