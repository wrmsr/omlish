# ruff: noqa: UP006 UP007
from omlish.lite.logs import log

from .dispatchers import Dispatchers
from .groups import ProcessGroupManager
from .poller import Poller
from .types import ExitNow


##


class IoManager:
    def __init__(
            self,
            *,
            poller: Poller,
            process_groups: ProcessGroupManager,
    ) -> None:
        super().__init__()

        self._poller = poller
        self._process_groups = process_groups

    def get_dispatchers(self) -> Dispatchers:
        return Dispatchers(
            d
            for p in self._process_groups.all_processes()
            for d in p.get_dispatchers()
        )

    def poll(self) -> None:
        dispatchers = self.get_dispatchers()

        for fd, dispatcher in dispatchers.items():
            if dispatcher.readable():
                self._poller.register_readable(fd)
            if dispatcher.writable():
                self._poller.register_writable(fd)

        timeout = 1  # this cannot be fewer than the smallest TickEvent (5)
        r, w = self._poller.poll(timeout)

        for fd in r:
            if fd in dispatchers:
                try:
                    dispatcher = dispatchers[fd]
                    log.debug('read event caused by %r', dispatcher)
                    dispatcher.handle_read_event()
                    if not dispatcher.readable():
                        self._poller.unregister_readable(fd)
                except ExitNow:
                    raise
                except Exception:  # noqa
                    dispatchers[fd].handle_error()
            else:
                # if the fd is not in combined map, we should unregister it. otherwise, it will be polled every
                # time, which may cause 100% cpu usage
                log.debug('unexpected read event from fd %r', fd)
                try:
                    self._poller.unregister_readable(fd)
                except Exception:  # noqa
                    pass

        for fd in w:
            if fd in dispatchers:
                try:
                    dispatcher = dispatchers[fd]
                    log.debug('write event caused by %r', dispatcher)
                    dispatcher.handle_write_event()
                    if not dispatcher.writable():
                        self._poller.unregister_writable(fd)
                except ExitNow:
                    raise
                except Exception:  # noqa
                    dispatchers[fd].handle_error()
            else:
                log.debug('unexpected write event from fd %r', fd)
                try:
                    self._poller.unregister_writable(fd)
                except Exception:  # noqa
                    pass
