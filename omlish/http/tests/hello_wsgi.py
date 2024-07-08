"""
https://asgi.readthedocs.io/_/downloads/en/latest/pdf/

REQUEST_METHOD is the method
SCRIPT_NAME is root_path
PATH_INFO can be derived by stripping root_path from path
QUERY_STRING is query_string
CONTENT_TYPE can be extracted from headers
CONTENT_LENGTH can be extracted from headers
SERVER_NAME and SERVER_PORT are in server
REMOTE_HOST/REMOTE_ADDR and REMOTE_PORT are in client
SERVER_PROTOCOL is encoded in http_version
wsgi.url_scheme is scheme
wsgi.input is a StringIO based around the http.request messages
wsgi.errors is directed by the wrapper as needed
"""
import http.server
import io
import typing as ta
import wsgiref.simple_server

from .. import consts


BytesLike: ta.TypeAlias = bytes | bytearray
Environ = ta.Mapping[str, ta.Any]
StartResponse = ta.Callable[[str, ta.Iterable[tuple[str, str]]], ta.Callable[[BytesLike], None]]
App = ta.Callable[[Environ, StartResponse], ta.Iterable[BytesLike]]


def demo_app(environ: Environ, start_response: StartResponse) -> ta.Iterable[BytesLike]:
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
        app: App,
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
