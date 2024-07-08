import io
import wsgiref.simple_server


def demo_app(environ, start_response):
    stdout = io.StringIO()
    print("Hello world!", file=stdout)
    print(file=stdout)
    h = sorted(environ.items())
    for k, v in h:
        print(k, '=', repr(v), file=stdout)
    start_response("200 OK", [('Content-Type', 'text/plain; charset=utf-8')])
    return [stdout.getvalue().encode("utf-8")]


def make_server(
        host,
        port,
        app,
        server_class=wsgiref.simple_server.WSGIServer,
        handler_class=wsgiref.simple_server.WSGIRequestHandler,
):
    server = server_class((host, port), handler_class)
    server.set_app(app)
    return server


if __name__ == '__main__':
    with make_server('', 8000, demo_app) as httpd:
        sa = httpd.socket.getsockname()
        print("Serving HTTP on", sa[0], "port", sa[1], "...")

        # import webbrowser
        # webbrowser.open('http://localhost:8000/xyz?abc')

        httpd.serve_forever()
