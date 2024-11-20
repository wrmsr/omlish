

class SayHiHttpRequestHandler(BaseHttpRequestHandler):
    def do_method(self) -> None:
        method = self.command
        path = self.path

        if (cl := self.headers.get('Content-Length')):
            data = self.rfile.read(int(cl))
        else:
            data = b''

        resp = '\n'.join([
            f'method: {method}',
            f'path: {path}',
            f'data: {len(data)}',
            '',
        ])

        resp_bytes = resp.encode('utf-8')
        self.send_response(http.HTTPStatus.OK)
        self.send_header(hc.HEADER_CONTENT_TYPE.decode(), hc.CONTENT_TYPE_TEXT.decode())
        self.send_header(hc.HEADER_CONTENT_LENGTH.decode(), str(len(resp_bytes)))
        self.end_headers()
        self.wfile.write(resp_bytes)

    do_GET = do_method
    do_POST = do_method


def _main() -> None:
    port = 8000
    bind = None

    ServerClass = http.server.ThreadingHTTPServer
    ServerClass.address_family, addr = _get_best_family(bind, port)

    with ServerClass(
            addr,
            functools.partial(
                SocketServerStreamRequestHandlerAdapter,
                adapter_target_cls=SayHiHttpRequestHandler,
            ),
    ) as httpd:
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
