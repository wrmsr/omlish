import datetime
import io
import typing as ta
import urllib.parse

from omlish import check
from omlish import codecs as cdu
from omlish import dataclasses as dc
from omlish import lang
from omlish.http import all as hu
from omlish.http.coro.server.simple import make_simple_http_server
from omlish.http.handlers import HttpHandlerRequest
from omlish.http.handlers import HttpHandlerResponse
from omlish.http.handlers import HttpHandlerResponseStreamedData
from omlish.io.coro import iterable_bytes_stepped_coro


##


class SimpleMitmHandler:
    DEFAULT_READ_SIZE: int = 65536

    @dc.dataclass(frozen=True)
    class Request:
        when: datetime.datetime
        request: HttpHandlerRequest

    @dc.dataclass(frozen=True)
    class Response:
        when: datetime.datetime
        response: HttpHandlerResponse
        data: bytes

    def __init__(
            self,
            target: str,
            *,
            client: hu.HttpClient | None = None,

            on_request: ta.Callable[[Request], None] | None = None,
            on_response: ta.Callable[[Request, Response], None] | None = None,
            on_error: ta.Callable[[Request, Exception], None] | None = None,

            handle_gzip: bool = False,
            read_size: int = DEFAULT_READ_SIZE,
    ) -> None:
        super().__init__()

        self._target = target

        if client is None:
            client = hu.client()
        self._client = client

        self._on_request = on_request
        self._on_response = on_response
        self._on_error = on_error

        self._handle_gzip = handle_gzip
        self._read_size = read_size

    def __call__(self, h_req: HttpHandlerRequest) -> HttpHandlerResponse:
        m_req = self.Request(
            lang.utcnow(),
            h_req,
        )

        try:
            if self._on_request is not None:
                self._on_request(m_req)

            url = self._target + h_req.path

            hdrs = hu.headers(h_req.headers)
            hdrs = hdrs.update(
                (b'Host', check.not_none(urllib.parse.urlparse(self._target).hostname).encode()),
                override=True,
            )

            t_resp = self._client.stream_request(hu.HttpRequest(
                    url,
                    h_req.method,
                    headers=hdrs,
                    data=h_req.data,
            ))

            try:
                dec: ta.Callable[[bytes], ta.Iterable[bytes]]
                if (
                        self._handle_gzip and
                        t_resp.headers is not None and
                        t_resp.headers.single_dct.get(b'content-encoding') == b'gzip'
                ):
                    dec = iterable_bytes_stepped_coro(
                        check.not_none(cdu.lookup('gzip').new_incremental)().decode_incremental(),
                    ).send
                else:
                    dec = lambda b: [b]

                buf: io.BytesIO | None = None
                if self._on_response is not None:
                    buf = io.BytesIO()

                resp_hdrs = dict(check.not_none(t_resp.headers).single_str_dct)
                is_chunked = resp_hdrs.get('transfer-encoding') == 'chunked'

                def stream_data():
                    try:
                        while b := t_resp.stream.read(self._read_size):
                            if buf is not None:
                                for o in dec(b):
                                    buf.write(o)

                            if is_chunked:
                                b = b''.join([f'{len(b):X}\r\n'.encode(), b, b'\r\n'])
                            yield b

                        if is_chunked:
                            yield b'0\r\n\r\n'

                        t_resp.close()

                    except Exception as e:
                        if self._on_error is not None:
                            self._on_error(m_req, e)
                        raise

                    else:
                        if self._on_response is not None:
                            self._on_response(
                                m_req,
                                self.Response(
                                    lang.utcnow(),
                                    h_resp,
                                    check.not_none(buf).getvalue(),
                                ),
                            )

                h_resp = HttpHandlerResponse(
                    t_resp.status,
                    resp_hdrs,
                    data=HttpHandlerResponseStreamedData(stream_data()),
                    # close_connection=True,
                )

                return h_resp

            except Exception:
                t_resp.close()
                raise

        except Exception as e:
            if self._on_error is not None:
                self._on_error(m_req, e)
            raise


##


def _main() -> None:
    default_port = 8080

    #

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('port_or_unix_socket', default=str(default_port), nargs='?')
    parser.add_argument('-x', '--httpx', action='store_true')
    parser.add_argument('-k', '--keep-alive', action='store_true')
    args = parser.parse_args()

    #

    port_or_unix_socket = check.non_empty_str(args.port_or_unix_socket)
    bind: ta.Any
    try:
        port = int(port_or_unix_socket)
    except ValueError:
        bind = check.non_empty_str(port_or_unix_socket)
    else:
        bind = port

    #

    def on_response(
            req: SimpleMitmHandler.Request,
            resp: SimpleMitmHandler.Response,
    ) -> None:
        print((req, resp))

    def on_error(
            req: SimpleMitmHandler.Request,
            exc: Exception,
    ) -> None:
        print((req, exc))

    handler = SimpleMitmHandler(
        args.target,
        client=hu.HttpxHttpClient() if args.httpx else None,
        handle_gzip=not args.httpx,
        on_response=on_response,
        on_error=on_error,
    )

    with make_simple_http_server(
            bind,
            handler,
            keep_alive=args.keep_alive,
            use_threads=True,
    ) as server:
        server.run()


if __name__ == '__main__':
    _main()
