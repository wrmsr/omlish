# ruff: noqa: UP006 UP007
# @omlish-lite
import socket


def close_socket_immediately(sock: socket.socket) -> None:
    try:
        # explicitly shutdown. socket.close() merely releases the socket and waits for GC to perform the actual close.
        sock.shutdown(socket.SHUT_WR)

    except OSError:
        # some platforms may raise ENOTCONN here
        pass

    sock.close()
