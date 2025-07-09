import io
import typing as ta
import urllib.parse

from omlish import check
from omlish import codecs as cdu
from omlish import dataclasses as dc
from omlish.http import all as hu
from omlish.http.coro.simple import make_simple_http_server
from omlish.http.handlers import HttpHandlerRequest
from omlish.http.handlers import HttpHandlerResponse
from omlish.http.handlers import HttpHandlerResponseStreamedData
from omlish.io.coro import iterable_bytes_stepped_coro


##


class SimpleMitmHandler:
    DEFAULT_READ_SIZE: int = 65536

    def __init__(
            self,
            target: str,
            *,
            on_request: ta.Callable[[HttpHandlerRequest], None] | None = None,
            on_response: ta.Callable[[HttpHandlerRequest, HttpHandlerResponse], None] | None = None,
            on_error: ta.Callable[[HttpHandlerRequest, Exception], None] | None = None,

            read_size: int = DEFAULT_READ_SIZE,
    ) -> None:
        super().__init__()

        self._target = target

        self._on_request = on_request
        self._on_response = on_response
        self._on_error = on_error

        self._read_size = read_size

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        try:
            if self._on_request is not None:
                self._on_request(req)

            url = self._target + req.path

            hdrs = hu.headers(req.headers)
            hdrs = hdrs.update(
                (b'Host', check.not_none(urllib.parse.urlparse(self._target).hostname).encode()),
                override=True,
            )

            tgt_resp = hu.client().stream_request(hu.HttpRequest(
                    url,
                    req.method,
                    headers=hdrs,
                    data=req.data,
            ))

            dec: ta.Callable[[bytes], ta.Iterable[bytes]]
            if tgt_resp.headers is not None and tgt_resp.headers.single_dct.get(b'content-encoding') == b'gzip':
                dec = iterable_bytes_stepped_coro(
                    check.not_none(cdu.lookup('gzip').new_incremental)().decode_incremental(),
                ).send
            else:
                dec = lambda b: [b]

            buf: io.BytesIO | None = None
            if self._on_response is not None:
                buf = io.BytesIO()

            try:
                def stream_data():
                    try:
                        while b := tgt_resp.stream.read(self._read_size):
                            if buf is not None:
                                for o in dec(b):
                                    buf.write(o)

                            yield b

                            tgt_resp.close()

                    except Exception as e:
                        if self._on_error is not None:
                            self._on_error(req, e)
                        raise

                    else:
                        if self._on_response is not None:
                            self._on_response(
                                req,
                                dc.replace(
                                    resp,
                                    data=check.not_none(buf).getvalue(),
                                ),
                            )

                resp = HttpHandlerResponse(
                    tgt_resp.status,
                    check.not_none(tgt_resp.headers).single_str_dct,
                    data=HttpHandlerResponseStreamedData(stream_data()),
                    # close_connection=True,
                )

                return resp

            except Exception:
                tgt_resp.close()
                raise

        except Exception as e:
            if self._on_error is not None:
                self._on_error(req, e)
            raise


##


def _main() -> None:
    default_port = 8080

    #

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('port_or_unix_socket', default=str(default_port), nargs='?')
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
            req: HttpHandlerRequest,
            resp: HttpHandlerResponse,
    ) -> None:
        print((req, resp))

    def on_error(
            req: HttpHandlerRequest,
            exc: Exception,
    ) -> None:
        print((req, exc))

    handler = SimpleMitmHandler(
        args.target,
        on_response=on_response,
        on_error=on_error,
    )

    with make_simple_http_server(
            bind,
            handler,
            use_threads=True,
    ) as server:
        server.run()


if __name__ == '__main__':
    _main()
