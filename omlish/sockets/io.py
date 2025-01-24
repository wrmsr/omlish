# ruff: noqa: UP006 UP007
# @omlish-lite
import io
import socket
import typing as ta


##


class SocketWriter(io.BufferedIOBase):
    """
    Simple writable BufferedIOBase implementation for a socket

    Does not hold data in a buffer, avoiding any need to call flush().
    """

    def __init__(self, sock):
        super().__init__()

        self._sock = sock

    def writable(self):
        return True

    def write(self, b):
        self._sock.sendall(b)
        with memoryview(b) as view:
            return view.nbytes

    def fileno(self):
        return self._sock.fileno()


class SocketIoPair(ta.NamedTuple):
    r: ta.BinaryIO
    w: ta.BinaryIO

    @classmethod
    def from_socket(
            cls,
            sock: socket.socket,
            *,
            r_buf_size: int = -1,
            w_buf_size: int = 0,
    ) -> 'SocketIoPair':
        rf: ta.Any = sock.makefile('rb', r_buf_size)

        if w_buf_size:
            wf: ta.Any = SocketWriter(sock)
        else:
            wf = sock.makefile('wb', w_buf_size)

        return cls(rf, wf)


##


def close_socket_immediately(sock: socket.socket) -> None:
    try:
        # Explicitly shutdown. socket.close() merely releases the socket and waits for GC to perform the actual close.
        sock.shutdown(socket.SHUT_WR)

    except OSError:
        # Some platforms may raise ENOTCONN here
        pass

    sock.close()
