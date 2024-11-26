# ruff: noqa: UP006 UP007
from .types import Dispatcher
from .types import ProcessOutputDispatcher
from .utils.collections import KeyedCollection
from .utils.ostypes import Fd


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
            if isinstance(d, ProcessOutputDispatcher):
                d.remove_logs()

    def reopen_logs(self) -> None:
        for d in self:
            if isinstance(d, ProcessOutputDispatcher):
                d.reopen_logs()
