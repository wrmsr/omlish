import functools
import select
import socket
import typing as ta


Addr: ta.TypeAlias = tuple[str, int]


class IoManager:
    def __init__(self) -> None:
        super().__init__()

        self._read_callbacks: dict[int, ta.Callable[[], None]] = {}
        self._write_callbacks: dict[int, ta.Callable[[], None]] = {}

    def unregister(
            self,
            *,
            r: ta.Iterable[int] = (),
            w: ta.Iterable[int] = (),
    ) -> None:
        for f in r:
            del self._read_callbacks[f]
        for f in w:
            del self._write_callbacks[f]

    def register(
            self,
            fn: ta.Callable[[], None],
            *,
            r: ta.Iterable[int] = (),
            w: ta.Iterable[int] = (),
    ) -> None:
        for f in r:
            self._read_callbacks[f] = fn
        for f in w:
            self._write_callbacks[f] = fn

    def poll(self, *, timeout: float = 1.) -> None:
        print(f'rd={sorted(self._read_callbacks)}')
        print(f'wd={sorted(self._read_callbacks)}')
        print()

        readable, writable, _ = select.select(
            self._read_callbacks,
            self._write_callbacks,
            [],
            timeout,
        )

        print(f'rl={sorted(readable)}')
        print(f'wl={sorted(writable)}')
        print()

        for rf in readable:
            self._read_callbacks[rf]()
        for wf in writable:
            self._write_callbacks[wf]()


class EchoServerConnection:
    def __init__(self, addr: Addr, sock: socket.socket, io: IoManager) -> None:
        super().__init__()
        self._addr = addr
        self._sock = sock
        self._io = io
        io.register(self._on_read, r=[sock.fileno()])

    def _on_read(self) -> None:
        buf = self._sock.recv(1024)
        if not buf:
            self._io.unregister(r=[self._sock.fileno()])
            self._sock.close()
            return
        self._sock.send(buf)


class EchoServer:
    def __init__(self, addr: Addr, io: IoManager) -> None:
        super().__init__()
        self._addr = addr
        self._io = io
        self._sock = socket.create_server(self._addr)
        self._sock.listen(1)
        io.register(self._on_conn, r=[self._sock.fileno()])

    def _on_conn(self) -> None:
        cli_sock, cli_addr = self._sock.accept()
        EchoServerConnection(cli_addr, cli_sock, self._io)



def _main() -> None:
    iom = IoManager()

    srv_addr = ('localhost', 9999)
    srv = EchoServer(srv_addr, iom)

    while True:
        iom.poll()


if __name__ == '__main__':
    _main()
