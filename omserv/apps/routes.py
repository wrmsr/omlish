"""
TODO:
 - include route in process_app?
  - or, deduplicate handlers and only process apps once?
"""
import contextlib
import dataclasses as dc
import logging
import typing as ta

from omlish import check
from omlish import lang
from omlish.http import asgi

from .base import BASE_SERVER_URL
from .base import SCOPE
from .base import BaseServerUrl
from .markers import AppMarker
from .markers import AppMarkerProcessor
from .markers import AppMarkerProcessorMap
from .markers import NopAppMarkerProcessor
from .markers import append_app_marker
from .markers import get_app_markers


log = logging.getLogger(__name__)


##


class Route(ta.NamedTuple):
    method: str
    path: str

    @classmethod
    def get(cls, path: str) -> 'Route':
        return cls('GET', path)

    @classmethod
    def post(cls, path: str) -> 'Route':
        return cls('POST', path)

    @classmethod
    def put(cls, path: str) -> 'Route':
        return cls('PUT', path)

    @classmethod
    def delete(cls, path: str) -> 'Route':
        return cls('DELETE', path)


class RouteHandler(ta.NamedTuple):
    route: Route
    handler: asgi.App


@dc.dataclass(frozen=True)
class _HandlesAppMarker(AppMarker, lang.Final):
    routes: ta.Sequence[Route]


def handles(*routes: Route):
    def inner(fn):
        append_app_marker(fn, _HandlesAppMarker(routes))
        return fn

    routes = tuple(map(check.of_isinstance(Route), routes))
    return inner


HANDLES_APP_MARKER_PROCESSORS: AppMarkerProcessorMap = {
    _HandlesAppMarker: NopAppMarkerProcessor(),
}


##


class RouteHandlerHolder(lang.Abstract):  # noqa
    def get_route_handlers(self) -> ta.Iterable[RouteHandler]:
        return get_marked_route_handlers(self)


def get_marked_route_handlers(h: RouteHandlerHolder) -> ta.Sequence[RouteHandler]:
    ret: list[RouteHandler] = []

    cdct: dict[str, ta.Any] = {}
    for mcls in reversed(type(h).__mro__):
        cdct.update(**mcls.__dict__)

    for att, obj in cdct.items():
        if not (mks := get_app_markers(obj)):
            continue
        if not (hms := [m for m in mks if isinstance(m, _HandlesAppMarker)]):
            continue
        if not (rs := [r for hm in hms for r in hm.routes]):
            continue

        app = getattr(h, att)
        ret.extend(RouteHandler(r, app) for r in rs)

    return ret


@dc.dataclass()
class DuplicateRouteError(Exception):
    route_handlers: ta.Sequence[RouteHandler]


def build_route_handler_map(
        handlers: ta.Iterable[RouteHandler | RouteHandlerHolder],
        processors: ta.Mapping[type[AppMarker], AppMarkerProcessor],
) -> ta.Mapping[Route, asgi.App]:
    rh_by_r: dict[Route, RouteHandler] = {}
    for h in handlers:
        if isinstance(h, RouteHandlerHolder):
            rhs = list(h.get_route_handlers())
        else:
            rhs = [h]

        for rh in rhs:
            try:
                ex = rh_by_r[rh.route]
            except KeyError:
                pass
            else:
                raise DuplicateRouteError([rh, ex])

            rh_by_r[rh.route] = rh

    app_by_r: dict[Route, asgi.App] = {}
    for r, rh in rh_by_r.items():
        app = rh.handler

        markers = get_app_markers(rh.handler)
        for m in markers:
            mp = processors[type(m)]
            if mp is not None:
                app = mp.process_app(app)

        app_by_r[r] = app

    return app_by_r


##


@dc.dataclass(frozen=True)
class RouteHandlerApp(asgi.App_):
    route_handlers: ta.Mapping[Route, asgi.App]
    base_server_url: BaseServerUrl | None = None

    URL_SCHEME_PORT_PAIRS: ta.ClassVar[ta.Collection[tuple[str, int]]] = (
        ('http', 80),
        ('https', 443),
    )

    async def __call__(self, scope: asgi.Scope, recv: asgi.Recv, send: asgi.Send) -> None:
        with contextlib.ExitStack() as es:
            es.enter_context(lang.context_var_setting(SCOPE, scope))  # noqa

            match scope_ty := scope['type']:
                case 'lifespan':
                    await asgi.stub_lifespan(scope, recv, send)
                    return

                case 'http':
                    if self.base_server_url is not None:
                        bsu = self.base_server_url
                    else:
                        sch = scope['scheme']
                        h, p = scope['server']
                        if (sch, p) not in self.URL_SCHEME_PORT_PAIRS:
                            ps = f':{p}'
                        else:
                            ps = ''
                        bsu = BaseServerUrl(f'{sch}://{h}{ps}/')
                    es.enter_context(lang.context_var_setting(BASE_SERVER_URL, bsu))  # noqa

                    route = Route(scope['method'], scope['raw_path'].decode())
                    handler = self.route_handlers.get(route)

                    if handler is not None:
                        await handler(scope, recv, send)

                    else:
                        await asgi.send_response(send, 404)

                case _:
                    raise ValueError(f'Unhandled scope type: {scope_ty!r}')
