# ruff: noqa: UP006 UP007
import errno
import select
import sys
import typing as ta

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

            self._kqueue: ta.Optional[ta.Any] = None

        #

        def _get_kqueue(self) -> 'select.kqueue':
            if (kq := self._kqueue) is not None:
                return kq
            kq = select.kqueue()
            self._kqueue = kq
            return kq

        def close(self) -> None:
            if self._kqueue is not None:
                self._kqueue.close()
                self._kqueue = None

        def reregister(self) -> None:
            for fd in self._readable:
                self.register_readable(fd)
            for fd in self._writable:
                self.register_writable(fd)

        #

        def register_readable(self, fd: int) -> None:
            if super().register_readable(fd):
                self._control(fd, select.KQ_FILTER_READ, select.KQ_EV_ADD)

        def register_writable(self, fd: int) -> None:
            if super().register_writable(fd):
                self._control(fd, select.KQ_FILTER_WRITE, select.KQ_EV_ADD)

        def unregister_readable(self, fd: int) -> None:
            if super().unregister_readable(fd):
                self._control(fd, select.KQ_FILTER_READ, select.KQ_EV_DELETE)

        def unregister_writable(self, fd: int) -> None:
            if super().unregister_writable(fd):
                self._control(fd, select.KQ_FILTER_WRITE, select.KQ_EV_DELETE)

        def _control(self, fd: int, filter: int, flags: int) -> None:  # noqa
            ke = select.kevent(fd, filter=filter, flags=flags)
            kq = self._get_kqueue()
            try:
                kq.control([ke], 0)  # type: ignore
            except OSError as error:
                if error.errno == errno.EBADF:
                    # log.debug('EBADF encountered in kqueue. Invalid file descriptor %s', ke.ident)
                    pass
                else:
                    raise

        #

        def poll(self, timeout: ta.Optional[float]) -> FdIoPoller.PollResult:
            try:
                kes = self._kqueue.control(None, self.max_events, timeout)  # type: ignore

            except OSError as exc:
                if exc.errno == errno.EINTR:
                    return FdIoPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
                else:
                    raise

            r: ta.List[int] = []
            w: ta.List[int] = []
            for ke in kes:
                if ke.filter == select.KQ_FILTER_READ:
                    r.append(ke.ident)
                if ke.filter == select.KQ_FILTER_WRITE:
                    w.append(ke.ident)

            return FdIoPoller.PollResult(r, w)


else:
    KqueuePoller = None
