# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import socket
import typing as ta

from .core import BlueletCoro
from .core import ReturnEvent
from .core import ValueEvent
from .core import spawn
from .events import Event
from .events import WaitableEvent
from .events import Waitables


##


class SocketClosedError(Exception):
    pass


class Listener:
    """A socket wrapper object for listening sockets."""

    def __init__(self, host: str, port: int) -> None:
        """Create a listening socket on the given hostname and port."""

        super().__init__()
        self._closed = False
        self.host = host
        self.port = port

        self.sock = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(5)

    def accept(self) -> Event:
        """
        An event that waits for a connection on the listening socket. When a connection is made, the event returns a
        Connection object.
        """

        if self._closed:
            raise SocketClosedError
        return AcceptEvent(self)

    def close(self) -> None:
        """Immediately close the listening socket. (Not an event.)"""

        self._closed = True
        self.sock.close()


class Connection:
    """A socket wrapper object for connected sockets."""

    def __init__(self, sock: socket.socket, addr: ta.Tuple[str, int]) -> None:
        super().__init__()
        self.sock = sock
        self.addr = addr
        self._buf = bytearray()
        self._closed: bool = False

    def close(self) -> None:
        """Close the connection."""

        self._closed = True
        self.sock.close()

    def recv(self, size: int) -> Event:
        """Read at most size bytes of data from the socket."""

        if self._closed:
            raise SocketClosedError

        if self._buf:
            # We already have data read previously.
            out = self._buf[:size]
            self._buf = self._buf[size:]
            return ValueEvent(bytes(out))
        else:
            return ReceiveEvent(self, size)

    def send(self, data: bytes) -> Event:
        """Sends data on the socket, returning the number of bytes successfully sent."""

        if self._closed:
            raise SocketClosedError
        return SendEvent(self, data)

    def sendall(self, data: bytes) -> Event:
        """Send all of data on the socket."""

        if self._closed:
            raise SocketClosedError
        return SendEvent(self, data, True)

    def readline(self, terminator: bytes = b'\n', bufsize: int = 1024) -> BlueletCoro:
        """Reads a line (delimited by terminator) from the socket."""

        if self._closed:
            raise SocketClosedError

        while True:
            if terminator in self._buf:
                line, self._buf = self._buf.split(terminator, 1)
                line += terminator
                yield ReturnEvent(bytes(line))
                break
            data = yield ReceiveEvent(self, bufsize)
            if data:
                self._buf += data
            else:
                line = self._buf
                self._buf = bytearray()
                yield ReturnEvent(bytes(line))
                break


##


class SocketEvent(Event, abc.ABC):  # noqa
    pass


#


@dc.dataclass(frozen=True, eq=False)
class AcceptEvent(WaitableEvent, SocketEvent):
    """An event for Listener objects (listening sockets) that suspends execution until the socket gets a connection."""

    listener: Listener

    def waitables(self) -> Waitables:
        return Waitables(r=[self.listener.sock])

    def fire(self) -> Connection:
        sock, addr = self.listener.sock.accept()
        return Connection(sock, addr)


#


@dc.dataclass(frozen=True, eq=False)
class ReceiveEvent(WaitableEvent, SocketEvent):
    """An event for Connection objects (connected sockets) for asynchronously reading data."""

    conn: Connection
    bufsize: int

    def waitables(self) -> Waitables:
        return Waitables(r=[self.conn.sock])

    def fire(self) -> bytes:
        return self.conn.sock.recv(self.bufsize)


#


@dc.dataclass(frozen=True, eq=False)
class SendEvent(WaitableEvent, SocketEvent):
    """An event for Connection objects (connected sockets) for asynchronously writing data."""

    conn: Connection
    data: bytes
    sendall: bool = False

    def waitables(self) -> Waitables:
        return Waitables(w=[self.conn.sock])

    def fire(self) -> ta.Optional[int]:
        if self.sendall:
            self.conn.sock.sendall(self.data)
            return None
        else:
            return self.conn.sock.send(self.data)


##


def connect(host: str, port: int) -> Event:
    """Event: connect to a network address and return a Connection object for communicating on the socket."""

    addr = (host, port)
    sock = socket.create_connection(addr)
    return ValueEvent(Connection(sock, addr))


def server(host: str, port: int, func) -> BlueletCoro:
    """
    A coroutine that runs a network server. Host and port specify the listening address. func should be a coroutine that
    takes a single parameter, a Connection object. The coroutine is invoked for every incoming connection on the
    listening socket.
    """

    def handler(conn):
        try:
            yield func(conn)
        finally:
            conn.close()

    listener = Listener(host, port)
    try:
        while True:
            conn = yield listener.accept()
            yield spawn(handler(conn))
    except KeyboardInterrupt:
        pass
    finally:
        listener.close()
