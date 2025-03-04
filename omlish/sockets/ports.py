# @omlish-lite
import socket


def get_available_port(host: str = '127.0.0.1') -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        sock.listen(1)
        port = sock.getsockname()[1]
    return port
