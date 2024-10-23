# ruff: noqa: UP006 UP007
import abc
import errno
import logging
import select
import sys
import typing as ta


log = logging.getLogger(__name__)


class BasePoller(abc.ABC):

    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    def register_readable(self, fd: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def register_writable(self, fd: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def unregister_readable(self, fd: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def unregister_writable(self, fd: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[int], ta.List[int]]:
        raise NotImplementedError

    def before_daemonize(self) -> None:  # noqa
        pass

    def after_daemonize(self) -> None:  # noqa
        pass

    def close(self) -> None:  # noqa
        pass


class SelectPoller(BasePoller):

    def __init__(self) -> None:
        super().__init__()

        self._readables: ta.Set[int] = set()
        self._writables: ta.Set[int] = set()

    def register_readable(self, fd: int) -> None:
        self._readables.add(fd)

    def register_writable(self, fd: int) -> None:
        self._writables.add(fd)

    def unregister_readable(self, fd: int) -> None:
        self._readables.discard(fd)

    def unregister_writable(self, fd: int) -> None:
        self._writables.discard(fd)

    def unregister_all(self) -> None:
        self._readables.clear()
        self._writables.clear()

    def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[int], ta.List[int]]:
        try:
            r, w, x = select.select(
                self._readables,
                self._writables,
                [], timeout,
            )
        except OSError as err:
            if err.args[0] == errno.EINTR:
                log.debug('EINTR encountered in poll')
                return [], []
            if err.args[0] == errno.EBADF:
                log.debug('EBADF encountered in poll')
                self.unregister_all()
                return [], []
            raise
        return r, w


class PollPoller(BasePoller):
    _READ = select.POLLIN | select.POLLPRI | select.POLLHUP
    _WRITE = select.POLLOUT

    def __init__(self) -> None:
        super().__init__()

        self._poller = select.poll()
        self._readables: set[int] = set()
        self._writables: set[int] = set()

    def register_readable(self, fd: int) -> None:
        self._poller.register(fd, self._READ)
        self._readables.add(fd)

    def register_writable(self, fd: int) -> None:
        self._poller.register(fd, self._WRITE)
        self._writables.add(fd)

    def unregister_readable(self, fd: int) -> None:
        self._readables.discard(fd)
        self._poller.unregister(fd)
        if fd in self._writables:
            self._poller.register(fd, self._WRITE)

    def unregister_writable(self, fd: int) -> None:
        self._writables.discard(fd)
        self._poller.unregister(fd)
        if fd in self._readables:
            self._poller.register(fd, self._READ)

    def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[int], ta.List[int]]:
        fds = self._poll_fds(timeout)  # type: ignore
        readables, writables = [], []
        for fd, eventmask in fds:
            if self._ignore_invalid(fd, eventmask):
                continue
            if eventmask & self._READ:
                readables.append(fd)
            if eventmask & self._WRITE:
                writables.append(fd)
        return readables, writables

    def _poll_fds(self, timeout: float) -> ta.List[ta.Tuple[int, int]]:
        try:
            return self._poller.poll(timeout * 1000)
        except OSError as err:
            if err.args[0] == errno.EINTR:
                log.debug('EINTR encountered in poll')
                return []
            raise

    def _ignore_invalid(self, fd: int, eventmask: int) -> bool:
        if eventmask & select.POLLNVAL:
            # POLLNVAL means `fd` value is invalid, not open. When a process quits it's `fd`s are closed so there is no
            # more reason to keep this `fd` registered If the process restarts it's `fd`s are registered again.
            self._poller.unregister(fd)
            self._readables.discard(fd)
            self._writables.discard(fd)
            return True
        return False


if sys.platform == 'darwin' or sys.platform.startswith('freebsd'):
    class KqueuePoller(BasePoller):
        max_events = 1000

        def __init__(self) -> None:
            super().__init__()

            self._kqueue: ta.Optional[ta.Any] = select.kqueue()
            self._readables: set[int] = set()
            self._writables: set[int] = set()

        def register_readable(self, fd: int) -> None:
            self._readables.add(fd)
            kevent = select.kevent(fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_ADD)
            self._kqueue_control(fd, kevent)

        def register_writable(self, fd: int) -> None:
            self._writables.add(fd)
            kevent = select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_ADD)
            self._kqueue_control(fd, kevent)

        def unregister_readable(self, fd: int) -> None:
            kevent = select.kevent(fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_DELETE)
            self._readables.discard(fd)
            self._kqueue_control(fd, kevent)

        def unregister_writable(self, fd: int) -> None:
            kevent = select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_DELETE)
            self._writables.discard(fd)
            self._kqueue_control(fd, kevent)

        def _kqueue_control(self, fd: int, kevent: 'select.kevent') -> None:
            try:
                self._kqueue.control([kevent], 0)  # type: ignore
            except OSError as error:
                if error.errno == errno.EBADF:
                    log.debug('EBADF encountered in kqueue. Invalid file descriptor %s', fd)
                else:
                    raise

        def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[int], ta.List[int]]:
            readables, writables = [], []  # type: ignore

            try:
                kevents = self._kqueue.control(None, self.max_events, timeout)  # type: ignore
            except OSError as error:
                if error.errno == errno.EINTR:
                    log.debug('EINTR encountered in poll')
                    return readables, writables
                raise

            for kevent in kevents:
                if kevent.filter == select.KQ_FILTER_READ:
                    readables.append(kevent.ident)
                if kevent.filter == select.KQ_FILTER_WRITE:
                    writables.append(kevent.ident)

            return readables, writables

        def before_daemonize(self) -> None:
            self.close()

        def after_daemonize(self) -> None:
            self._kqueue = select.kqueue()
            for fd in self._readables:
                self.register_readable(fd)
            for fd in self._writables:
                self.register_writable(fd)

        def close(self) -> None:
            self._kqueue.close()  # type: ignore
            self._kqueue = None

else:
    KqueuePoller = None


Poller: ta.Type[BasePoller]
if (
        sys.platform == 'darwin' or sys.platform.startswith('freebsd') and
        hasattr(select, 'kqueue') and KqueuePoller is not None
):
    Poller = KqueuePoller
elif hasattr(select, 'poll'):
    Poller = PollPoller
else:
    Poller = SelectPoller
