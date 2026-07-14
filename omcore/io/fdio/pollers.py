# ruff: noqa: UP006 UP007 UP045
import abc
import dataclasses as dc
import errno
import select
import typing as ta

from ...lite.abstract import Abstract


##


class FdioPoller(Abstract):
    def __init__(self) -> None:
        super().__init__()

        self._readable: ta.Set[int] = set()
        self._writable: ta.Set[int] = set()

    #

    def close(self) -> None:  # noqa
        pass

    def reopen(self) -> None:  # noqa
        pass

    #

    @property
    @ta.final
    def readable(self) -> ta.AbstractSet[int]:
        return self._readable

    @property
    @ta.final
    def writable(self) -> ta.AbstractSet[int]:
        return self._writable

    #

    @ta.final
    def register_readable(self, fd: int) -> bool:
        if fd in self._readable:
            return False
        self._register_readable(fd)
        self._readable.add(fd)
        return True

    @ta.final
    def register_writable(self, fd: int) -> bool:
        if fd in self._writable:
            return False
        self._register_writable(fd)
        self._writable.add(fd)
        return True

    @ta.final
    def unregister_readable(self, fd: int) -> bool:
        if fd not in self._readable:
            return False
        self._readable.discard(fd)
        self._unregister_readable(fd)
        return True

    @ta.final
    def unregister_writable(self, fd: int) -> bool:
        if fd not in self._writable:
            return False
        self._writable.discard(fd)
        self._unregister_writable(fd)
        return True

    #

    def _register_readable(self, fd: int) -> None:  # noqa
        pass

    def _register_writable(self, fd: int) -> None:  # noqa
        pass

    def _unregister_readable(self, fd: int) -> None:  # noqa
        pass

    def _unregister_writable(self, fd: int) -> None:  # noqa
        pass

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
    class PollResult:
        r: ta.Sequence[int] = ()
        w: ta.Sequence[int] = ()

        inv: ta.Sequence[int] = ()

        msg: ta.Optional[str] = None
        exc: ta.Optional[BaseException] = None

    @abc.abstractmethod
    def poll(self, timeout: ta.Optional[float]) -> PollResult:
        raise NotImplementedError


##


class SelectFdioPoller(FdioPoller):
    def poll(self, timeout: ta.Optional[float]) -> FdioPoller.PollResult:
        try:
            r, w, x = select.select(
                self._readable,
                self._writable,
                [],
                timeout,
            )

        except OSError as exc:
            if exc.errno == errno.EINTR:
                return FdioPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
            elif exc.errno == errno.EBADF:
                return FdioPoller.PollResult(msg='EBADF encountered in poll', exc=exc)
            else:
                raise

        return FdioPoller.PollResult(r, w)


##


PollFdioPoller: ta.Optional[ta.Type[FdioPoller]]
if hasattr(select, 'poll'):

    class _PollFdioPoller(FdioPoller):
        def __init__(self) -> None:
            super().__init__()

            self._poller = select.poll()

        #

        def _register_readable(self, fd: int) -> None:
            self._update_registration(fd, r=True, w=fd in self._writable)

        def _register_writable(self, fd: int) -> None:
            self._update_registration(fd, r=fd in self._readable, w=True)

        def _unregister_readable(self, fd: int) -> None:
            self._update_registration(fd, r=False, w=False)

        def _unregister_writable(self, fd: int) -> None:
            self._update_registration(fd, r=fd in self._readable, w=False)

        #

        _READ = select.POLLIN | select.POLLPRI | select.POLLHUP
        _WRITE = select.POLLOUT

        def _update_registration(self, fd: int, *, r: bool, w: bool) -> None:
            if r or w:
                self._poller.register(fd, (self._READ if r else 0) | (self._WRITE if w else 0))
            else:
                self._poller.unregister(fd)

        #

        def poll(self, timeout: ta.Optional[float]) -> FdioPoller.PollResult:
            polled: ta.List[ta.Tuple[int, int]]
            try:
                polled = self._poller.poll(timeout * 1000 if timeout is not None else None)

            except OSError as exc:
                if exc.errno == errno.EINTR:
                    return FdioPoller.PollResult(msg='EINTR encountered in poll', exc=exc)
                else:
                    raise

            r: ta.List[int] = []
            w: ta.List[int] = []
            inv: ta.List[int] = []
            for fd, mask in polled:
                if mask & select.POLLNVAL:
                    self._poller.unregister(fd)
                    self._readable.discard(fd)
                    self._writable.discard(fd)
                    inv.append(fd)
                    continue
                if mask & self._READ:
                    r.append(fd)
                if mask & self._WRITE:
                    w.append(fd)
            return FdioPoller.PollResult(r, w, inv=inv)

    PollFdioPoller = _PollFdioPoller
else:
    PollFdioPoller = None
