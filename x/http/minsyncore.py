import socket


def _main() -> None:
    srv_addr = ('localhost', 9999)
    srv_sock = socket.create_server(srv_addr)
    srv_sock.listen(1)
    while True:
        cli_sock, cli_addr = srv_sock.accept()
        while True:
            buf = cli_sock.recv(1024)
            if not buf:
                break
            cli_sock.send(buf)
        cli_sock.close()


if __name__ == '__main__':
    _main()
