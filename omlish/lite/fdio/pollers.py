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

    def close(self) -> None:  # noqa
        pass

    #

    @property
    def readable(self) -> ta.AbstractSet[int]:
        return self._readable

    @property
    def writable(self) -> ta.AbstractSet[int]:
        return self._writable

    #

    def register_readable(self, fd: int) -> bool:
        if fd in self._readable:
            return False
        self._readable.add(fd)
        return True

    def register_writable(self, fd: int) -> bool:
        if fd in self._writable:
            return False
        self._writable.add(fd)
        return True

    def unregister_readable(self, fd: int) -> bool:
        if fd not in self._readable:
            return False
        self._readable.discard(fd)
        return True

    def unregister_writable(self, fd: int) -> bool:
        if fd not in self._writable:
            return False
        self._writable.discard(fd)
        return True

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
            if exc.errno == errno.EINTR:
                return FdIoPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
            elif exc.errno == errno.EBADF:
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
        if super().register_readable(fd):
            self._poller.register(fd, self._READ)

    def register_writable(self, fd: int) -> None:
        if super().register_writable(fd):
            self._poller.register(fd, self._WRITE)

    def unregister_readable(self, fd: int) -> None:
        if super().unregister_readable(fd):
            self._poller.unregister(fd)
            if fd in self._writable:
                self._poller.register(fd, self._WRITE)

    def unregister_writable(self, fd: int) -> None:
        if super().unregister_writable(fd):
            self._poller.unregister(fd)
            if fd in self._readable:
                self._poller.register(fd, self._READ)

    #

    def poll(self, timeout: ta.Optional[float]) -> FdIoPoller.PollResult:
        polled: ta.List[ta.Tuple[int, int]]
        try:
            polled = self._poller.poll(timeout * 1000 if timeout is not None else None)

        except OSError as exc:
            if exc.errno == errno.EINTR:
                return FdIoPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
            else:
                raise

        r: ta.List[int] = []
        w: ta.List[int] = []
        for fd, mask in polled:
            if self._ignore_invalid(fd, mask):
                continue
            if mask & self._READ:
                r.append(fd)
            if mask & self._WRITE:
                w.append(fd)
        return FdIoPoller.PollResult(r, w)

    def _ignore_invalid(self, fd: int, mask: int) -> bool:
        if mask & select.POLLNVAL:
            # POLLNVAL means `fd` value is invalid, not open. When a process quits it's `fd`s are closed so there is no
            # more reason to keep this `fd` registered If the process restarts it's `fd`s are registered again.
            self._poller.unregister(fd)
            self._readable.discard(fd)
            self._writable.discard(fd)
            return True

        return False
