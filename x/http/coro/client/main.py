import errno
import socket
import typing as ta

from omlish.lite.check import check

from .client import HttpConnection
from .client import HttpResponse
from .io import CloseIo
from .io import ConnectIo
from .io import Io
from .io import ReadIo
from .io import ReadLineIo
from .io import WriteIo


##


def _main3() -> None:
    import urllib.request
    req = urllib.request.Request('https://www.baidu.com')
    with urllib.request.urlopen(req) as resp:  # noqa
        print(resp.read())


def _main2() -> None:
    conn_cls = __import__('http.client').client.HTTPConnection

    url = 'www.example.com'
    conn = conn_cls(url)

    conn.request('GET', '/')
    r1 = conn.get_response() if hasattr(conn, 'get_response') else conn.getresponse()  # noqa
    print((r1.status, r1.reason))

    # data1 = r1.read()

    while chunk := r1.read(200):
        print(repr(chunk))


def _main() -> None:
    conn_cls = HttpConnection

    url = 'www.example.com'
    conn = conn_cls(url)

    sock: ta.Optional[socket.socket] = None
    sock_file: ta.Optional = None

    def handle_io(o: Io) -> ta.Any:
        nonlocal sock
        nonlocal sock_file

        if isinstance(o, ConnectIo):
            check.none(sock)
            sock = socket.create_connection(*o.args, **o.kwargs)

            # Might fail in OSs that don't implement TCP_NODELAY
            try:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except OSError as e:
                if e.errno != errno.ENOPROTOOPT:
                    raise

            sock_file = sock.makefile('rb')

            return None

        elif isinstance(o, CloseIo):
            check.not_none(sock).close()
            return None

        elif isinstance(o, WriteIo):
            check.not_none(sock).sendall(o.data)
            return None

        elif isinstance(o, ReadIo):
            if (sz := o.sz) is not None:
                return check.not_none(sock_file).read(sz)
            else:
                return check.not_none(sock_file).read()

        elif isinstance(o, ReadLineIo):
            return check.not_none(sock_file).readline(o.sz)

        else:
            raise TypeError(o)

    resp: ta.Optional[HttpResponse] = None

    def get_resp():
        nonlocal resp
        resp = yield from conn.get_response()

    def print_resp():
        d = yield from check.not_none(resp).read()
        print(d)

    for f in [
        conn.connect,
        lambda: conn.request('GET', '/'),
        get_resp,
        print_resp,
        conn.close,
    ]:
        g = f()
        i = None
        while True:
            try:
                o = g.send(i)
            except StopIteration:
                break
            i = handle_io(o)

    # conn.request('GET', '/')
    # r1 = conn.get_response() if hasattr(conn, 'get_response') else conn.getresponse()  # noqa
    # print((r1.status, r1.reason))
    #
    # # data1 = r1.read()
    #
    # while chunk := r1.read(200):
    #     print(repr(chunk))


if __name__ == '__main__':
    _main()
