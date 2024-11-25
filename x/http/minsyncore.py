import functools
import select
import socket
import typing as ta


def _main() -> None:
    rd: dict[int, ta.Callable[[], None]] = {}
    wd: dict[int, ta.Callable[[], None]] = {}

    #

    def cli_sock_on_read(sock: socket.socket) -> None:
        buf = sock.recv(1024)
        if not buf:
            del rd[sock.fileno()]
            sock.close()
            return
        sock.send(buf)

    #

    def srv_sock_on_read(sock: socket.socket) -> None:
        cli_sock, cli_addr = sock.accept()
        rd[cli_sock.fileno()] = functools.partial(cli_sock_on_read, cli_sock)

    srv_addr = ('localhost', 9999)
    srv_sock = socket.create_server(srv_addr)
    srv_sock.listen(1)
    rd[srv_sock.fileno()] = functools.partial(srv_sock_on_read, srv_sock)

    #

    while True:
        print(f'rd={sorted(rd)}')
        print(f'wd={sorted(wd)}')
        print()

        rl, wl, _ = select.select(
            rd,
            wd,
            [],
            1.,
        )

        print(f'rl={sorted(rl)}')
        print(f'wl={sorted(wl)}')
        print()

        for rf in rl:
            rd[rf]()
        for wf in wl:
            wd[wf]()


if __name__ == '__main__':
    _main()
