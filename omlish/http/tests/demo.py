# ruff: noqa: UP006 UP007 UP045
"""
Todo:
 - x/http/htt/omni/socketbinding.py

socat TCP-LISTEN:8000,fork UNIX-CONNECT:foo.sock
"""
import typing as ta

from ... import check
from ..coro.server.server import UnsupportedMethodHttpHandlerError
from ..coro.server.simple import make_simple_http_server
from ..handlers import HttpHandlerRequest
from ..handlers import HttpHandlerResponse
from ..handlers import HttpHandlerResponseStreamedData


##


def say_hi_handler(req: HttpHandlerRequest) -> HttpHandlerResponse:
    if req.method not in ('GET', 'POST'):
        raise UnsupportedMethodHttpHandlerError

    resp = '\n'.join([
        f'method: {req.method}',
        f'path: {req.path}',
        f'data: {len(req.data or b"")}',
        '',
    ])
    data = resp.encode('utf-8')

    resp_data: ta.Any
    if 'stream' in req.headers:
        def stream_data():
            for b in data:
                yield bytes([b])

        resp_data = HttpHandlerResponseStreamedData(
            stream_data(),
            len(data),
        )

    else:
        resp_data = data

    return HttpHandlerResponse(
        200,
        data=resp_data,
    )


##


def _main() -> None:
    default_port = 8000

    #

    import argparse

    parser = argparse.ArgumentParser()
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

    with make_simple_http_server(
        bind,
        say_hi_handler,
        use_threads=True,
    ) as server:
        server.run()


if __name__ == '__main__':
    _main()
