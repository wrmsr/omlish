# ruff: noqa: UP006 UP007
from .collections import KeyedCollection
from .ostypes import Fd
from .types import Dispatcher
from .types import OutputDispatcher


class Dispatchers(KeyedCollection[Fd, Dispatcher]):
    def _key(self, v: Dispatcher) -> Fd:
        return v.fd

    #

    def drain(self) -> None:
        for d in self:
            # note that we *must* call readable() for every dispatcher, as it may have side effects for a given
            # dispatcher (eg. call handle_listener_state_change for event listener processes)
            if d.readable():
                d.handle_read_event()
            if d.writable():
                d.handle_write_event()

    #

    def remove_logs(self) -> None:
        for d in self:
            if isinstance(d, OutputDispatcher):
                d.remove_logs()

    def reopen_logs(self) -> None:
        for d in self:
            if isinstance(d, OutputDispatcher):
                d.reopen_logs()
