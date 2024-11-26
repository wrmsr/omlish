# ruff: noqa: UP006 UP007
import abc
import errno
import select
import sys
import typing as ta

from omlish.lite.logs import log

from .setup import DaemonizeListener
from .utils.ostypes import Fd


class Poller(DaemonizeListener, abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    def register_readable(self, fd: Fd) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def register_writable(self, fd: Fd) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def unregister_readable(self, fd: Fd) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def unregister_writable(self, fd: Fd) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[Fd], ta.List[Fd]]:
        raise NotImplementedError

    def before_daemonize(self) -> None:  # noqa
        pass

    def after_daemonize(self) -> None:  # noqa
        pass

    def close(self) -> None:  # noqa
        pass


class SelectPoller(Poller):
    def __init__(self) -> None:
        super().__init__()

        self._readable: ta.Set[Fd] = set()
        self._writable: ta.Set[Fd] = set()

    def register_readable(self, fd: Fd) -> None:
        self._readable.add(fd)

    def register_writable(self, fd: Fd) -> None:
        self._writable.add(fd)

    def unregister_readable(self, fd: Fd) -> None:
        self._readable.discard(fd)

    def unregister_writable(self, fd: Fd) -> None:
        self._writable.discard(fd)

    def unregister_all(self) -> None:
        self._readable.clear()
        self._writable.clear()

    def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[Fd], ta.List[Fd]]:
        try:
            r, w, x = select.select(
                self._readable,
                self._writable,
                [], timeout,
            )
        except OSError as exc:
            if exc.args[0] == errno.EINTR:
                log.debug('EINTR encountered in poll')
                return [], []
            if exc.args[0] == errno.EBADF:
                log.debug('EBADF encountered in poll')
                self.unregister_all()
                return [], []
            raise
        return r, w


class PollPoller(Poller):
    _READ = select.POLLIN | select.POLLPRI | select.POLLHUP
    _WRITE = select.POLLOUT

    def __init__(self) -> None:
        super().__init__()

        self._poller = select.poll()
        self._readable: set[Fd] = set()
        self._writable: set[Fd] = set()

    def register_readable(self, fd: Fd) -> None:
        self._poller.register(fd, self._READ)
        self._readable.add(fd)

    def register_writable(self, fd: Fd) -> None:
        self._poller.register(fd, self._WRITE)
        self._writable.add(fd)

    def unregister_readable(self, fd: Fd) -> None:
        self._readable.discard(fd)
        self._poller.unregister(fd)
        if fd in self._writable:
            self._poller.register(fd, self._WRITE)

    def unregister_writable(self, fd: Fd) -> None:
        self._writable.discard(fd)
        self._poller.unregister(fd)
        if fd in self._readable:
            self._poller.register(fd, self._READ)

    def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[Fd], ta.List[Fd]]:
        fds = self._poll_fds(timeout)  # type: ignore
        readable, writable = [], []
        for fd, eventmask in fds:
            if self._ignore_invalid(fd, eventmask):
                continue
            if eventmask & self._READ:
                readable.append(fd)
            if eventmask & self._WRITE:
                writable.append(fd)
        return readable, writable

    def _poll_fds(self, timeout: float) -> ta.List[ta.Tuple[Fd, Fd]]:
        try:
            return self._poller.poll(timeout * 1000)  # type: ignore
        except OSError as exc:
            if exc.args[0] == errno.EINTR:
                log.debug('EINTR encountered in poll')
                return []
            raise

    def _ignore_invalid(self, fd: Fd, eventmask: int) -> bool:
        if eventmask & select.POLLNVAL:
            # POLLNVAL means `fd` value is invalid, not open. When a process quits it's `fd`s are closed so there is no
            # more reason to keep this `fd` registered If the process restarts it's `fd`s are registered again.
            self._poller.unregister(fd)
            self._readable.discard(fd)
            self._writable.discard(fd)
            return True
        return False


if sys.platform == 'darwin' or sys.platform.startswith('freebsd'):
    class KqueuePoller(Poller):
        max_events = 1000

        def __init__(self) -> None:
            super().__init__()

            self._kqueue: ta.Optional[ta.Any] = select.kqueue()
            self._readable: set[Fd] = set()
            self._writable: set[Fd] = set()

        def register_readable(self, fd: Fd) -> None:
            self._readable.add(fd)
            kevent = select.kevent(fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_ADD)
            self._kqueue_control(fd, kevent)

        def register_writable(self, fd: Fd) -> None:
            self._writable.add(fd)
            kevent = select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_ADD)
            self._kqueue_control(fd, kevent)

        def unregister_readable(self, fd: Fd) -> None:
            kevent = select.kevent(fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_DELETE)
            self._readable.discard(fd)
            self._kqueue_control(fd, kevent)

        def unregister_writable(self, fd: Fd) -> None:
            kevent = select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_DELETE)
            self._writable.discard(fd)
            self._kqueue_control(fd, kevent)

        def _kqueue_control(self, fd: Fd, kevent: 'select.kevent') -> None:
            try:
                self._kqueue.control([kevent], 0)  # type: ignore
            except OSError as error:
                if error.errno == errno.EBADF:
                    log.debug('EBADF encountered in kqueue. Invalid file descriptor %s', fd)
                else:
                    raise

        def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[Fd], ta.List[Fd]]:
            readable, writable = [], []  # type: ignore

            try:
                kevents = self._kqueue.control(None, self.max_events, timeout)  # type: ignore
            except OSError as error:
                if error.errno == errno.EINTR:
                    log.debug('EINTR encountered in poll')
                    return readable, writable
                raise

            for kevent in kevents:
                if kevent.filter == select.KQ_FILTER_READ:
                    readable.append(kevent.ident)
                if kevent.filter == select.KQ_FILTER_WRITE:
                    writable.append(kevent.ident)

            return readable, writable

        def before_daemonize(self) -> None:
            self.close()

        def after_daemonize(self) -> None:
            self._kqueue = select.kqueue()
            for fd in self._readable:
                self.register_readable(fd)
            for fd in self._writable:
                self.register_writable(fd)

        def close(self) -> None:
            self._kqueue.close()  # type: ignore
            self._kqueue = None

else:
    KqueuePoller = None


def get_poller_impl() -> ta.Type[Poller]:
    if (
            (sys.platform == 'darwin' or sys.platform.startswith('freebsd')) and
            hasattr(select, 'kqueue') and
            KqueuePoller is not None
    ):
        return KqueuePoller
    elif hasattr(select, 'poll'):
        return PollPoller
    else:
        return SelectPoller
