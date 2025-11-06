import typing as ta

from ... import flasky


def wsgiref_app_runner(params: flasky.AppRunParams) -> None:
    import wsgiref.simple_server  # noqa

    from ....http import consts  # noqa
    from ....http import wsgi  # noqa

    def app_fn(environ: wsgi.Environ, start_response: wsgi.StartResponse) -> ta.Iterable[bytes]:
        path = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']

        route = params.app.routes_by_key.get(flasky.RouteKey(path, method))
        if route is None:
            start_response(consts.STATUS_NOT_FOUND, [])
            return []

        view_func = params.app.view_funcs_by_endpoint[route.endpoint]

        request = flasky.Request(
            path=path,
            method=method,
        )

        with flasky.Cvs.REQUEST.set(request):
            for brf in params.app.before_request_funcs:
                if (response := brf()) is not None:
                    break

            if response is None:
                out = view_func()

                response = flasky.Response(out)

                # short-circuited if before_request_funcs returned something
                for arf in params.app.after_request_funcs:
                    response = arf(response)

        start_response(
            consts.STATUS_OK,
            [
                (consts.HEADER_CONTENT_TYPE.decode(), consts.CONTENT_TYPE_TEXT_UTF8.decode()),  # noqa
            ],
        )

        return [out.encode('utf-8')]

    server = wsgiref.simple_server.WSGIServer(
        ('', params.port or 8000),
        wsgiref.simple_server.WSGIRequestHandler,  # noqa
    )
    server.set_app(app_fn)  # type: ignore

    with server as httpd:
        sa = httpd.socket.getsockname()
        print('Serving HTTP on', sa[0], 'port', sa[1], '...')

        httpd.serve_forever()


##


def _main() -> None:
    from .app import run_app  # noqa

    with flasky.Cvs.APP_RUNNER.set(wsgiref_app_runner):
        run_app(flasky.Api())


if __name__ == '__main__':
    _main()
