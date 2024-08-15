import socket


def _main():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('', 4915))
    listener.listen(1)
    while True:
        sock, addr = listener.accept()
        while True:
            data = sock.recv(1024)
            if not data:
                break
            sock.sendall(data)


if __name__ == '__main__':
    _main()
