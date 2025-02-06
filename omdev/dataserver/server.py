# ruff: noqa: UP006 UP007
import dataclasses as dc
import http.client
import typing as ta

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
            routes: ta.Optional[ta.Iterable[HandlerRoute]] = None,
            config: Config = Config(),
    ) -> None:
        super().__init__()

        self._config = config

        self.set_routes(routes)

    #

    _routes_by_path: ta.Dict[str, HandlerRoute]

    def set_routes(self, routes: ta.Optional[ta.Iterable[HandlerRoute]]) -> None:
        routes_by_path: ta.Dict[str, DataServer.HandlerRoute] = {}

        for r in routes or []:
            for p in r.paths:
                check.not_in(p, routes_by_path)
                routes_by_path[p] = r

        self._routes_by_path = routes_by_path

    #

    def handle(self, req: DataServerRequest) -> DataServerResponse:
        try:
            rt = self._routes_by_path[req.path]
        except KeyError:
            return DataServerResponse(http.HTTPStatus.NOT_FOUND)

        return rt.handler.handle(req)
