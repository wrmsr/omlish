# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
# Based on bluelet ( https://github.com/sampsyo/bluelet ) by Adrian Sampson, original license:
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import dataclasses as dc
import socket
import typing as ta

from omlish.lite.abstract import Abstract

from .core import BlueletCoro
from .core import ReturnBlueletEvent
from .core import ValueBlueletEvent
from .core import _CoreBlueletApi
from .events import BlueletEvent
from .events import BlueletWaitables
from .events import WaitableBlueletEvent


##


class SocketClosedBlueletError(Exception):
    pass


class BlueletListener:
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

    def accept(self) -> 'AcceptBlueletEvent':
        """
        An event that waits for a connection on the listening socket. When a connection is made, the event returns a
        Connection object.
        """

        if self._closed:
            raise SocketClosedBlueletError
        return AcceptBlueletEvent(self)

    def close(self) -> None:
        """Immediately close the listening socket. (Not an event.)"""

        self._closed = True
        self.sock.close()


class BlueletConnection:
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

    def recv(self, size: int) -> BlueletEvent:
        """Read at most size bytes of data from the socket."""

        if self._closed:
            raise SocketClosedBlueletError

        if self._buf:
            # We already have data read previously.
            out = self._buf[:size]
            self._buf = self._buf[size:]
            return ValueBlueletEvent(bytes(out))
        else:
            return ReceiveBlueletEvent(self, size)

    def send(self, data: bytes) -> BlueletEvent:
        """Sends data on the socket, returning the number of bytes successfully sent."""

        if self._closed:
            raise SocketClosedBlueletError
        return SendBlueletEvent(self, data)

    def sendall(self, data: bytes) -> BlueletEvent:
        """Send all of data on the socket."""

        if self._closed:
            raise SocketClosedBlueletError
        return SendBlueletEvent(self, data, True)

    def readline(self, terminator: bytes = b'\n', bufsize: int = 1024) -> BlueletCoro:
        """Reads a line (delimited by terminator) from the socket."""

        if self._closed:
            raise SocketClosedBlueletError

        while True:
            if terminator in self._buf:
                line, self._buf = self._buf.split(terminator, 1)
                line += terminator
                yield ReturnBlueletEvent(bytes(line))
                break

            if (data := (yield ReceiveBlueletEvent(self, bufsize))):
                self._buf += data
            else:
                line = self._buf
                self._buf = bytearray()
                yield ReturnBlueletEvent(bytes(line))
                break


##


class SocketBlueletEvent(BlueletEvent, Abstract):
    pass


@dc.dataclass(frozen=True, eq=False)
class AcceptBlueletEvent(WaitableBlueletEvent, SocketBlueletEvent):
    """An event for Listener objects (listening sockets) that suspends execution until the socket gets a connection."""

    listener: BlueletListener

    def waitables(self) -> BlueletWaitables:
        return BlueletWaitables(r=[self.listener.sock])

    def fire(self) -> BlueletConnection:
        sock, addr = self.listener.sock.accept()
        return BlueletConnection(sock, addr)


@dc.dataclass(frozen=True, eq=False)
class ReceiveBlueletEvent(WaitableBlueletEvent, SocketBlueletEvent):
    """An event for Connection objects (connected sockets) for asynchronously reading data."""

    conn: BlueletConnection
    bufsize: int

    def waitables(self) -> BlueletWaitables:
        return BlueletWaitables(r=[self.conn.sock])

    def fire(self) -> bytes:
        return self.conn.sock.recv(self.bufsize)


@dc.dataclass(frozen=True, eq=False)
class SendBlueletEvent(WaitableBlueletEvent, SocketBlueletEvent):
    """An event for Connection objects (connected sockets) for asynchronously writing data."""

    conn: BlueletConnection
    data: bytes
    sendall: bool = False

    def waitables(self) -> BlueletWaitables:
        return BlueletWaitables(w=[self.conn.sock])

    def fire(self) -> ta.Optional[int]:
        if self.sendall:
            self.conn.sock.sendall(self.data)
            return None
        else:
            return self.conn.sock.send(self.data)


##


class _SocketsBlueletApi(_CoreBlueletApi):
    def connect(self, host: str, port: int) -> BlueletEvent:
        """Event: connect to a network address and return a Connection object for communicating on the socket."""

        addr = (host, port)
        sock = socket.create_connection(addr)
        return ValueBlueletEvent(BlueletConnection(sock, addr))

    def server(self, host: str, port: int, func) -> BlueletCoro:
        """
        A coroutine that runs a network server. Host and port specify the listening address. func should be a coroutine
        that takes a single parameter, a Connection object. The coroutine is invoked for every incoming connection on
        the listening socket.
        """

        def handler(conn):
            try:
                yield func(conn)
            finally:
                conn.close()

        listener = BlueletListener(host, port)
        try:
            while True:
                conn = yield listener.accept()
                yield self.spawn(handler(conn))
        except KeyboardInterrupt:
            pass
        finally:
            listener.close()
