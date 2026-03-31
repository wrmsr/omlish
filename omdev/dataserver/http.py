# ruff: noqa: UP006 UP007 UP045
"""
TODO:
 - asyncio
 - chunked transfer - both output and urllib input
 - range headers
"""
import typing as ta

from omlish.http.simple.handlers import SimpleHttpHandler_
from omlish.http.simple.handlers import SimpleHttpHandlerRequest
from omlish.http.simple.handlers import SimpleHttpHandlerResponse
from omlish.http.simple.handlers import SimpleHttpHandlerResponseStreamedData

from .handlers import DataServerRequest
from .server import DataServer


##


class DataServerSimpleHttpHandler(SimpleHttpHandler_):
    DEFAULT_READ_CHUNK_SIZE = 0x10000

    def __init__(
            self,
            ps: DataServer,
            *,
            read_chunk_size: int = DEFAULT_READ_CHUNK_SIZE,
    ) -> None:
        super().__init__()

        self._ps = ps
        self._read_chunk_size = read_chunk_size

    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        p_req = DataServerRequest(
            req.method,
            req.path,
        )

        p_resp = self._ps.handle(p_req)
        try:
            data: ta.Any
            if (p_body := p_resp.body) is not None:
                def stream_data():
                    try:
                        while (b := p_body.read(self._read_chunk_size)):
                            yield b
                    finally:
                        p_body.close()

                data = SimpleHttpHandlerResponseStreamedData(stream_data())

            else:
                data = None

            resp = SimpleHttpHandlerResponse(
                status=p_resp.status,
                headers=p_resp.headers,
                data=data,
                close_connection=True,
            )

            return resp

        except Exception:  # noqa
            p_resp.close()

            raise
