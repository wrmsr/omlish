# ruff: noqa: UP006 UP007
"""
TODO:
 - asyncio
 - chunked transfer - both output and urllib input
"""
import dataclasses as dc
import http.client
import typing as ta

from omlish.http.coro.simple import make_simple_http_server
from omlish.http.handlers import HttpHandler_
from omlish.http.handlers import HttpHandlerRequest
from omlish.http.handlers import HttpHandlerResponse
from omlish.http.handlers import HttpHandlerResponseStreamedData
from omlish.lite.check import check

from .handlers import DataServerHandler
from .handlers import DataServerRequest
from .handlers import DataServerResponse
from .handlers import DataServerTargetHandler
from .routes import DataServerRoute


##


class DataServer:
    @dc.dataclass(frozen=True)
    class HandlerRoute:
        paths: ta.Sequence[str]
        handler: DataServerHandler

        def __post_init__(self) -> None:
            check.not_isinstance(self.paths, str)
            for p in self.paths:
                check.non_empty_str(p)
            check.isinstance(self.handler, DataServerHandler)

        @classmethod
        def of(cls, obj: ta.Union[
            'DataServer.HandlerRoute',
            DataServerRoute,
        ]) -> 'DataServer.HandlerRoute':
            if isinstance(obj, cls):
                return obj

            elif isinstance(obj, DataServerRoute):
                return cls(
                    paths=obj.paths,
                    handler=DataServerTargetHandler.for_target(obj.target),
                )

            else:
                raise TypeError(obj)

        @classmethod
        def of_(cls, *objs: ta.Any) -> ta.List['DataServer.HandlerRoute']:
            return [cls.of(obj) for obj in objs]

    #

    @dc.dataclass(frozen=True)
    class Config:
        pass

    def __init__(
            self,
            routes: ta.Iterable[HandlerRoute],
            config: Config = Config(),
    ) -> None:
        super().__init__()

        self._config = config
        self._routes = list(routes)

        routes_by_path: dict[str, DataServer.Route] = {}
        for r in self._routes:
            for p in r.paths:
                check.not_in(p, routes_by_path)
                routes_by_path[p] = r
        self._routes_by_path = routes_by_path

    def handle(self, req: DataServerRequest) -> DataServerResponse:
        try:
            rt = self._routes_by_path[req.path]
        except KeyError:
            return DataServerResponse(http.HTTPStatus.NOT_FOUND)

        return rt.handler.handle(req)


##


class DataServerHttpHandler(HttpHandler_):
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

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
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

                data = HttpHandlerResponseStreamedData(stream_data())

            else:
                data = None

            resp = HttpHandlerResponse(
                status=p_resp.status,
                headers=p_resp.headers,
                data=data,
                close_connection=True,
            )

            return resp

        except Exception:  # noqa
            p_resp.close()

            raise


##


def _main() -> None:
    rts = [
        ('/hi', BytesDataServerTarget(data=b'hi!')),
        ('/src', FileDataServerTarget(file_path=__file__)),
        ('/google', UrlDataServerTarget(url='https://www.google.com/', methods=['GET'])),
    ]

    ps = DataServer(DataServer.build_routes(*rts))

    for req in [
        DataServerRequest('HEAD', '/hi'),
        DataServerRequest('GET', '/hi'),
        DataServerRequest('HEAD', '/src'),
        DataServerRequest('GET', '/src'),
        DataServerRequest('GET', '/google'),
    ]:
        with ps.handle(req) as resp:
            print(resp)

    #

    with make_simple_http_server(
            5021,
            DataServerHttpHandler(ps),
            use_threads=True,
    ) as server:
        server.run()


if __name__ == '__main__':
    _main()
