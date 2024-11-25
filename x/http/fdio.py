import abc
import errno
import select
import socket
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.check import check_none
from omlish.lite.check import check_not_none
from omlish.lite.http.coroserver import CoroHttpServer
from omlish.lite.http.handlers import HttpHandler
from omlish.lite.http.handlers import HttpHandlerRequest
from omlish.lite.http.handlers import HttpHandlerResponse
from omlish.lite.io import IncrementalWriteBuffer
from omlish.lite.io import ReadableListBuffer
from omlish.lite.socket import SocketAddress


Fd = ta.NewType('Fd', int)


##


class FdIoHandler(abc.ABC):
    @abc.abstractmethod
    def fd(self) -> Fd:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def closed(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    #

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return False

    #

    def on_readable(self) -> None:
        raise TypeError

    def on_writable(self) -> None:
        raise TypeError

    def on_error(self) -> None:
        pass


class SocketFdIoHandler(FdIoHandler, abc.ABC):
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._sock: ta.Optional[socket.socket] = sock

    def fd(self) -> Fd:
        return Fd(check_not_none(self._sock).fileno())

    @property
    def closed(self) -> bool:
        return self._sock is None

    def close(self) -> None:
        if self._sock is not None:
            self._sock.close()
        self._sock = None


##


class FdIoPoller(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

        self._readable: ta.Set[Fd] = set()
        self._writable: ta.Set[Fd] = set()

    #

    @property
    def readable(self) -> ta.AbstractSet[Fd]:
        return self._readable

    @property
    def writable(self) -> ta.AbstractSet[Fd]:
        return self._writable

    #

    def unregister_all(self) -> None:
        self._readable.clear()
        self._writable.clear()

    def register_readable(self, fd: Fd) -> None:
        self._readable.add(fd)

    def register_writable(self, fd: Fd) -> None:
        self._writable.add(fd)

    def unregister_readable(self, fd: Fd) -> None:
        self._readable.discard(fd)

    def unregister_writable(self, fd: Fd) -> None:
        self._writable.discard(fd)

    #

    def update(
            self,
            r: ta.AbstractSet[Fd],
            w: ta.AbstractSet[Fd],
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

    class PollResult(ta.NamedTuple):
        r: ta.List[Fd]
        w: ta.List[Fd]

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
                # log.debug('EINTR encountered in poll')
                return FdIoPoller.PollResult([], [])
            elif exc.args[0] == errno.EBADF:
                # log.debug('EBADF encountered in poll')
                self.unregister_all()
                return FdIoPoller.PollResult([], [])
            else:
                raise
        return FdIoPoller.PollResult(r, w)


##


class FdIoManager:
    def __init__(
            self,
            poller: FdIoPoller,
    ) -> None:
        super().__init__()

        self._poller = poller

        self._handlers: list[FdIoHandler] = []

    def register(self, h: FdIoHandler) -> None:
        self._handlers.append(h)

    def poll(self, *, timeout: float = 1.) -> None:
        hs = self._handlers
        rd = {h.fd(): h for h in hs if h.readable()}
        wd = {h.fd(): h for h in hs if h.writable()}

        self._poller.update(set(rd), set(wd))

        pr = self._poller.poll(timeout)

        for f in pr.r:
            if not (h := rd[f]).closed:
                h.on_readable()
        for f in pr.w:
            if not (h := wd[f]).closed:
                h.on_writable()

        self._handlers = [h for h in hs if not h.closed]
