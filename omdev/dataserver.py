# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - chunked transfer - both output and urllib input
"""
import abc
import dataclasses as dc
import http.client
import io
import os
import typing as ta
import urllib.request

from omlish.http.coro.simple import make_simple_http_server
from omlish.http.handlers import HttpHandler_
from omlish.http.handlers import HttpHandlerRequest
from omlish.http.handlers import HttpHandlerResponse
from omlish.http.handlers import HttpHandlerResponseStreamedData
from omlish.lite.check import check
from omlish.lite.dataclasses import dataclass_maybe_post_init


DataServerTargetT = ta.TypeVar('DataServerTargetT', bound='DataServerTarget')


##


@dc.dataclass(frozen=True)
class DataServerTarget(abc.ABC):  # noqa
    content_type: ta.Optional[str] = None
    content_length: ta.Optional[int] = None


@dc.dataclass(frozen=True)
class BytesDataServerTarget(DataServerTarget):
    data: ta.Optional[bytes] = None


@dc.dataclass(frozen=True)
class FileDataServerTarget(DataServerTarget):
    file_path: ta.Optional[str] = None

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        check.non_empty_str(self.file_path)


@dc.dataclass(frozen=True)
class UrlDataServerTarget(DataServerTarget):
    url: ta.Optional[str] = None
    methods: ta.Optional[ta.Container[str]] = None

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        check.non_empty_str(self.url)
        check.not_none(self.methods)
        check.not_isinstance(self.methods, str)


##


@dc.dataclass(frozen=True)
class DataServerRequest:
    method: str
    path: str


@dc.dataclass(frozen=True)
class DataServerResponse:
    status: int
    headers: ta.Optional[ta.Mapping[str, str]] = None
    body: ta.Optional[io.IOBase] = None

    #

    def close(self) -> None:
        if (body := self.body) is not None:
            body.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DataServerError(Exception):
    pass


class DataServerHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        raise NotImplementedError


##


class DataServerTargetHandler(DataServerHandler, abc.ABC, ta.Generic[DataServerTargetT]):
    def __init__(self, target: DataServerTargetT) -> None:
        super().__init__()

        self._target = target

    #

    @classmethod
    def for_target(cls, tgt: DataServerTarget, **kwargs: ta.Any) -> 'DataServerTargetHandler':
        try:
            hc = _DATA_SERVER_TARGET_HANDLERS[type(tgt)]
        except KeyError:
            raise TypeError(tgt)  # noqa
        else:
            return hc(tgt, **kwargs)

    #

    def _make_headers(self) -> ta.Dict[str, str]:
        dct = {}
        if (ct := self._target.content_type) is not None:
            dct['Content-Type'] = ct
        if (cl := self._target.content_length) is not None:
            dct['Content-Length'] = str(cl)
        return dct


#


_DATA_SERVER_TARGET_HANDLERS: ta.Dict[ta.Type[DataServerTarget], ta.Type[DataServerTargetHandler]] = {}


def _register_data_server_target_handler(*tcs):
    def inner(hc):
        check.issubclass(hc, DataServerTargetHandler)
        for tc in tcs:
            check.issubclass(tc, DataServerTarget)
            check.not_in(tc, _DATA_SERVER_TARGET_HANDLERS)
            _DATA_SERVER_TARGET_HANDLERS[tc] = hc
        return hc
    return inner


#


@_register_data_server_target_handler(BytesDataServerTarget)
class BytesDataServerTargetHandler(DataServerTargetHandler[BytesDataServerTarget]):
    def _make_headers(self) -> ta.Dict[str, str]:
        dct = super()._make_headers()
        if 'Content-Length' not in dct and self._target.data is not None:
            dct['Content-Length'] = str(len(self._target.data))
        return dct

    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method not in ('GET', 'HEAD'):
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)

        return DataServerResponse(
            http.HTTPStatus.OK,
            headers=self._make_headers(),
            body=io.BytesIO(self._target.data) if self._target.data is not None and req.method == 'GET' else None,
        )


#


@_register_data_server_target_handler(FileDataServerTarget)
class FileDataServerTargetHandler(DataServerTargetHandler[FileDataServerTarget]):
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method == 'HEAD':
            try:
                st = os.stat(check.not_none(self._target.file_path))
            except FileNotFoundError:
                return DataServerResponse(http.HTTPStatus.NOT_FOUND)

            return DataServerResponse(
                http.HTTPStatus.OK,
                headers={
                    'Content-Length': str(st.st_size),
                    **self._make_headers(),
                },
            )

        elif req.method == 'GET':
            try:
                f = open(check.not_none(self._target.file_path), 'rb')  # noqa
            except FileNotFoundError:
                return DataServerResponse(http.HTTPStatus.NOT_FOUND)

            try:
                sz = os.fstat(f.fileno())

                return DataServerResponse(
                    http.HTTPStatus.OK,
                    headers={
                        'Content-Length': str(sz.st_size),
                        **self._make_headers(),
                    },
                    body=f,  # noqa
                )

            except Exception:  # noqa
                f.close()
                raise

        else:
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)


#


@_register_data_server_target_handler(UrlDataServerTarget)
class UrlDataServerTargetHandler(DataServerTargetHandler[UrlDataServerTarget]):
    def handle(self, req: DataServerRequest) -> DataServerResponse:
        if req.method not in check.not_none(self._target.methods):
            return DataServerResponse(http.HTTPStatus.METHOD_NOT_ALLOWED)

        resp: http.client.HTTPResponse = urllib.request.urlopen(urllib.request.Request(  # noqa
            method=req.method,
            url=check.not_none(self._target.url),
        ))

        try:
            return DataServerResponse(
                resp.status,
                headers=dict(resp.headers.items()),
                body=resp,
            )

        except Exception:  # noqa
            resp.close()
            raise


##


class DataServer:
    @dc.dataclass(frozen=True)
    class Route:
        paths: ta.Sequence[str]
        handler: DataServerHandler

        def __post_init__(self) -> None:
            check.not_isinstance(self.paths, str)
            for p in self.paths:
                check.non_empty_str(p)
            check.isinstance(self.handler, DataServerHandler)

    @classmethod
    def build_route(cls, obj: ta.Union[
        Route,
        ta.Tuple[
            ta.Union[str, ta.Iterable[str]],
            ta.Union[DataServerTarget, DataServerTargetHandler],
        ],
    ]) -> Route:
        if isinstance(obj, cls.Route):
            return obj

        elif isinstance(obj, tuple):
            p, h = obj

            if isinstance(p, str):
                p = [p]

            if isinstance(h, DataServerTarget):
                h = DataServerTargetHandler.for_target(h)

            return DataServer.Route(tuple(p), h)

        else:
            raise TypeError(obj)

    @classmethod
    def build_routes(cls, *objs: ta.Any) -> ta.List[Route]:
        return [cls.build_route(obj) for obj in objs]

    #

    @dc.dataclass(frozen=True)
    class Config:
        pass

    def __init__(
            self,
            routes: ta.Iterable[Route],
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
