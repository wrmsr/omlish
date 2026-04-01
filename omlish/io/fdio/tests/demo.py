import socket
import typing as ta

from ....lite.check import check
from ....sockets.addresses import SocketAddress
from ..handlers import SocketFdioHandler
from ..kqueue import KqueueFdioPoller  # noqa
from ..manager import FdioManager
from ..pollers import FdioPoller
from ..pollers import PollFdioPoller  # noqa
from ..pollers import SelectFdioPoller


##


class SocketServerFdioHandler(SocketFdioHandler):
    def __init__(
            self,
            addr: SocketAddress,
            on_connect: ta.Callable[[socket.socket, SocketAddress], None],
    ) -> None:
        sock = socket.create_server(addr)
        sock.setblocking(False)

        super().__init__(addr, sock)

        self._on_connect = on_connect

        sock.listen(1)

    def readable(self) -> bool:
        return True

    def on_readable(self) -> None:
        cli_sock, cli_addr = check.not_none(self._sock).accept()
        cli_sock.setblocking(False)

        self._on_connect(cli_sock, cli_addr)


def _main() -> None:
    poller: FdioPoller = next(filter(None, [
        KqueueFdioPoller,
        PollFdioPoller,
        SelectFdioPoller,
    ]))()

    man = FdioManager(poller)

    def on_connect(sock: socket.socket, addr: SocketAddress) -> None:
        pass

    server = SocketServerFdioHandler(('127.0.0.1', 8080), on_connect)

    man.register(server)

    while True:
        man.poll()


if __name__ == '__main__':
    _main()
