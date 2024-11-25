# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import errno
import select
import typing as ta


##


class FdIoPoller(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

        self._readable: ta.Set[int] = set()
        self._writable: ta.Set[int] = set()

    #

    @property
    def readable(self) -> ta.AbstractSet[int]:
        return self._readable

    @property
    def writable(self) -> ta.AbstractSet[int]:
        return self._writable

    #

    def register_readable(self, fd: int) -> None:
        self._readable.add(fd)

    def register_writable(self, fd: int) -> None:
        self._writable.add(fd)

    def unregister_readable(self, fd: int) -> None:
        self._readable.discard(fd)

    def unregister_writable(self, fd: int) -> None:
        self._writable.discard(fd)

    #

    def update(
            self,
            r: ta.AbstractSet[int],
            w: ta.AbstractSet[int],
    ) -> None:
        for f in r - self._readable:
            self.register_readable(f)
        for f in w - self._writable:
            self.register_writable(f)
        for f in self._readable - r:
            self.unregister_readable(f)
        for f in self._writable - w:
            self.unregister_writable(f)

    #

    def close(self) -> None:  # noqa
        pass

    #

    @dc.dataclass(frozen=True)
    class PollResult(ta.NamedTuple):
        r: ta.Sequence[int] = ()
        w: ta.Sequence[int] = ()

        msg: ta.Optional[str] = None
        exc: ta.Optional[BaseException] = None

    @abc.abstractmethod
    def poll(self, timeout: ta.Optional[float]) -> PollResult:
        raise NotImplementedError


##


class SelectFdIoPoller(FdIoPoller):
    def poll(self, timeout: ta.Optional[float]) -> FdIoPoller.PollResult:
        try:
            r, w, x = select.select(
                self._readable,
                self._writable,
                [],
                timeout,
            )

        except OSError as exc:
            if exc.args[0] == errno.EINTR:
                return FdIoPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
            elif exc.args[0] == errno.EBADF:
                return FdIoPoller.PollResult(msg='EBADF encountered in poll', exc=exc)
            else:
                raise

        return FdIoPoller.PollResult(r, w)


##


class PollFdIoPoller(FdIoPoller):
    def __init__(self) -> None:
        super().__init__()

        self._poller = select.poll()

    #

    _READ = select.POLLIN | select.POLLPRI | select.POLLHUP
    _WRITE = select.POLLOUT

    def register_readable(self, fd: int) -> None:
        super().register_readable(fd)
        self._poller.register(fd, self._READ)

    def register_writable(self, fd: int) -> None:
        super().register_writable(fd)
        self._poller.register(fd, self._WRITE)

    def unregister_readable(self, fd: int) -> None:
        super().unregister_readable(fd)
        self._poller.unregister(fd)
        if fd in self._writable:
            self._poller.register(fd, self._WRITE)

    def unregister_writable(self, fd: int) -> None:
        super().unregister_writable(fd)
        self._poller.unregister(fd)
        if fd in self._readable:
            self._poller.register(fd, self._READ)

    #

    def poll(self, timeout: ta.Optional[float]) -> FdIoPoller.PollResult:
        fds: ta.List[ta.Tuple[int, int]]
        try:
            fds = self._poller.poll(timeout * 1000 if timeout is not None else None)
        except OSError as exc:
            if exc.args[0] == errno.EINTR:
                return FdIoPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
            else:
                raise

        r, w = [], []
        for fd, eventmask in fds:
            if self._ignore_invalid(fd, eventmask):
                continue
            if eventmask & self._READ:
                r.append(fd)
            if eventmask & self._WRITE:
                w.append(fd)

        return FdIoPoller.PollResult(r, w)

    def _ignore_invalid(self, fd: int, eventmask: int) -> bool:
        if not (eventmask & select.POLLNVAL):
            return  False

        # POLLNVAL means `fd` value is invalid, not open. When a process quits it's `fd`s are closed so there is no
        # more reason to keep this `fd` registered If the process restarts it's `fd`s are registered again.
        self._poller.unregister(fd)
        self._readable.discard(fd)
        self._writable.discard(fd)
        return True
