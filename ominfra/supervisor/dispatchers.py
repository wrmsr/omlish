# ruff: noqa: UP006 UP007 UP045
from omlish.io.fdio.handlers import FdioHandler

from .types import ProcessOutputDispatcher
from .utils.collections import KeyedCollection
from .utils.ostypes import Fd


##


class Dispatchers(KeyedCollection[Fd, FdioHandler]):
    def _key(self, v: FdioHandler) -> Fd:
        return Fd(v.fd())

    #

    def drain(self) -> None:
        for d in self:
            # note that we *must* call readable() for every dispatcher, as it may have side effects for a given
            # dispatcher (eg. call handle_listener_state_change for event listener processes)
            if d.readable():
                d.on_readable()
            if d.writable():
                d.on_writable()

    #

    def remove_logs(self) -> None:
        for d in self:
            if isinstance(d, ProcessOutputDispatcher):
                d.remove_logs()

    def reopen_logs(self) -> None:
        for d in self:
            if isinstance(d, ProcessOutputDispatcher):
                d.reopen_logs()
