import http.server
import io
import typing as ta
import wsgiref.simple_server

from .. import consts
from .. import wsgi


def demo_app(environ: wsgi.Environ, start_response: wsgi.StartResponse) -> ta.Iterable[bytes]:
    if environ['PATH_INFO'] == '/favicon.ico' and environ['REQUEST_METHOD'] == 'GET':
        start_response(consts.STATUS_NOT_FOUND, [])
        return []

    out = io.StringIO()

    print('Hello world!', file=out)
    print(file=out)

    h = sorted(environ.items())
    for k, v in h:
        print(k, '=', repr(v), file=out)

    start_response(consts.STATUS_OK, [(consts.HEADER_CONTENT_TYPE, consts.CONTENT_TYPE_TEXT_UTF8)])
    return [out.getvalue().encode('utf-8')]


def make_wsgiref_server(
        host: str,
        port: int,
        app: wsgi.App,
        server_class: type[wsgiref.simple_server.WSGIServer] = wsgiref.simple_server.WSGIServer,
        handler_class: type[wsgiref.simple_server.WSGIRequestHandler] = wsgiref.simple_server.WSGIRequestHandler,
) -> http.server.HTTPServer:
    server = server_class((host, port), handler_class)  # noqa
    server.set_app(app)  # type: ignore
    return server


def _main() -> None:
    with make_wsgiref_server('', 8000, demo_app) as httpd:
        sa = httpd.socket.getsockname()
        print('Serving HTTP on', sa[0], 'port', sa[1], '...')

        # import webbrowser
        # webbrowser.open('http://localhost:8000/xyz?abc')

        httpd.serve_forever()


if __name__ == '__main__':
    _main()
