# ruff: noqa: UP006 UP007
import errno
import select
import typing as ta
import sys

from .pollers import FdIoPoller


if sys.platform == 'darwin' or sys.platform.startswith('freebsd'):
    class KqueueFdIoPoller(FdIoPoller):
        DEFAULT_MAX_EVENTS = 1000

        def __init__(
                self,
                *,
                max_events: int = DEFAULT_MAX_EVENTS,
        ) -> None:
            super().__init__()

            self._max_events = max_events

            self._kqueue: ta.Optional[ta.Any] = select.kqueue()

        #

        def register_readable(self, fd: int) -> None:
            super().register_readable(fd)
            ke = select.kevent(fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_ADD)
            self._kqueue_control(fd, ke)

        def register_writable(self, fd: int) -> None:
            super().register_writable(fd)
            ke = select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_ADD)
            self._kqueue_control(fd, ke)

        def unregister_readable(self, fd: int) -> None:
            super().unregister_readable(fd)
            ke = select.kevent(fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_DELETE)
            self._kqueue_control(fd, ke)

        def unregister_writable(self, fd: int) -> None:
            super().unregister_writable(fd)
            ke = select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_DELETE)
            self._kqueue_control(fd, ke)

        #

        def close(self) -> None:
            self._kqueue.close()  # type: ignore
            self._kqueue = None

        #

        def poll(self, timeout: ta.Optional[float]) -> Poller.PollResult:
            r: ta.List[int] = []
            w: ta.List[int] = []

            try:
                kes = self._kqueue.control(None, self.max_events, timeout)  # type: ignore
            except OSError as exc:
                if exc.errno == errno.EINTR:
                    return FdIoPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
                raise

            for ke in kes:
                if ke.filter == select.KQ_FILTER_READ:
                    r.append(ke.ident)
                if ke.filter == select.KQ_FILTER_WRITE:
                    writable.append(ke.ident)

            return FdIoPoller.PollResult(r, writable)

        def _kqueue_control(self, fd: int, ke: 'select.kevent') -> None:
            try:
                self._kqueue.control([ke], 0)  # type: ignore
            except OSError as error:
                if error.errno == errno.EBADF:
                    log.debug('EBADF encountered in kqueue. Invalid file descriptor %s', fd)
                else:
                    raise

        #

        def before_daemonize(self) -> None:
            self.close()

        def after_daemonize(self) -> None:
            self._kqueue = select.kqueue()
            for fd in self._readable:
                self.register_readable(fd)
            for fd in self._writable:
                self.register_writable(fd)

else:
    KqueuePoller = None
