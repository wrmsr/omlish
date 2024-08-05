import contextlib
import dataclasses as dc
import os
import socket
import stat
import typing as ta

from .config import Config


@dc.dataclass()
class Sockets:
    insecure_sockets: list[socket.socket]


SocketKind: ta.TypeAlias = int | socket.SocketKind


class SocketTypeError(Exception):
    def __init__(self, expected: SocketKind, actual: SocketKind) -> None:
        super().__init__(
            f'Unexpected socket type, wanted "{socket.SocketKind(expected)}" got "{socket.SocketKind(actual)}"',
        )


def _create_sockets(
        config: Config,
        binds: ta.Sequence[str],
        type_: int = socket.SOCK_STREAM,
) -> list[socket.socket]:
    sockets: list[socket.socket] = []
    for bind in binds:
        binding: ta.Any = None

        if bind.startswith('unix:'):
            sock = socket.socket(socket.AF_UNIX, type_)
            binding = bind[5:]
            try:
                if stat.S_ISSOCK(os.stat(binding).st_mode):
                    os.remove(binding)
            except FileNotFoundError:
                pass

        elif bind.startswith('fd://'):
            sock = socket.socket(fileno=int(bind[5:]))
            actual_type = sock.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
            if actual_type != type_:
                raise SocketTypeError(type_, actual_type)

        else:
            bind = bind.replace('[', '').replace(']', '')
            try:
                value = bind.rsplit(':', 1)
                host, port = value[0], int(value[1])
            except (ValueError, IndexError):
                host, port = bind, 8000
            sock = socket.socket(socket.AF_INET6 if ':' in host else socket.AF_INET, type_)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if config.workers:
                with contextlib.suppress(AttributeError):
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            binding = (host, port)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if bind.startswith('unix:'):
            if config.umask is not None:
                current_umask = os.umask(config.umask)
            sock.bind(binding)
            if config.user is not None and config.group is not None:
                os.chown(binding, config.user, config.group)
            if config.umask is not None:
                os.umask(current_umask)

        elif bind.startswith('fd://'):
            pass

        else:
            sock.bind(binding)

        sock.setblocking(False)
        with contextlib.suppress(AttributeError):
            sock.set_inheritable(True)
        sockets.append(sock)

    return sockets


def create_sockets(config: Config) -> Sockets:
    insecure_sockets = _create_sockets(config, config.bind)
    return Sockets(insecure_sockets)


def repr_socket_addr(family: int, address: tuple) -> str:
    if family == socket.AF_INET:
        return f'{address[0]}:{address[1]}'
    elif family == socket.AF_INET6:
        return f'[{address[0]}]:{address[1]}'
    elif family == socket.AF_UNIX:
        return f'unix:{address}'
    else:
        return f'{address}'


def parse_socket_addr(family: int, address: tuple) -> tuple[str, int] | None:
    if family == socket.AF_INET:
        return address
    elif family == socket.AF_INET6:
        return (address[0], address[1])
    else:
        return None
