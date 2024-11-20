import http.server
import socket
import sys

from omlish.http import consts as hc


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        out = b'hi'

        self.send_response(http.HTTPStatus.OK)
        self.send_header(hc.HEADER_CONTENT_TYPE.decode(), hc.CONTENT_TYPE_TEXT.decode())
        self.send_header(hc.HEADER_CONTENT_LENGTH.decode(), str(len(out)))
        self.end_headers()
        self.wfile.write(out)


def _get_best_family(*address):
    infos = socket.getaddrinfo(
        *address,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    family, type, proto, canonname, sockaddr = next(iter(infos))
    return family, sockaddr


def _main() -> None:
    port = 8000
    bind = None
    protocol = 'HTTP/1.0'

    ServerClass = http.server.ThreadingHTTPServer
    HandlerClass = SimpleHTTPRequestHandler

    ServerClass.address_family, addr = _get_best_family(bind, port)
    HandlerClass.protocol_version = protocol
    with ServerClass(addr, HandlerClass) as httpd:
        host, port = httpd.socket.getsockname()[:2]
        url_host = f'[{host}]' if ':' in host else host
        print(f'Serving HTTP on {host} port {port} (http://{url_host}:{port}/) ...')

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nKeyboard interrupt received, exiting.')
            sys.exit(0)


if __name__ == '__main__':
    _main()
