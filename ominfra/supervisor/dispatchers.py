# ruff: noqa: UP006 UP007
from .collections import KeyedCollection
from .types import Dispatcher


class Dispatchers(KeyedCollection[int, Dispatcher]):
    def _key(self, v: Dispatcher) -> int:
        return v.fd

    #

    def drain(self) -> None:
        for dispatcher in self:
            # note that we *must* call readable() for every dispatcher, as it may have side effects for a given
            # dispatcher (eg. call handle_listener_state_change for event listener processes)
            if dispatcher.readable():
                dispatcher.handle_read_event()
            if dispatcher.writable():
                dispatcher.handle_write_event()

    #

    def remove_logs(self) -> None:
        for dispatcher in self:
            if hasattr(dispatcher, 'remove_logs'):
                dispatcher.remove_logs()

    def reopen_logs(self) -> None:
        for dispatcher in self:
            if hasattr(dispatcher, 'reopen_logs'):
                dispatcher.reopen_logs()
