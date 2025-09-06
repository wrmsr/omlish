"""
TODO:
 - include route in process_app?
  - or, deduplicate handlers and only process apps once?
"""
import contextlib
import dataclasses as dc
import re
import typing as ta

from omlish import check
from omlish import lang
from omlish.http import asgi
from omlish.logs import all as logs

from .base import BASE_SERVER_URL
from .base import SCOPE
from .base import BaseServerUrl
from .markers import AppMarker
from .markers import AppMarkerProcessor
from .markers import AppMarkerProcessorMap
from .markers import NopAppMarkerProcessor
from .markers import append_app_marker
from .markers import get_app_markers


CallableT = ta.TypeVar('CallableT', bound=ta.Callable)


KnownMethod: ta.TypeAlias = ta.Literal[
    'DELETE',
    'GET',
    'HEAD',
    'PATCH',
    'POST',
    'PUT',
]

KNOWN_METHODS: tuple[str, ...] = (
    'DELETE',
    'GET',
    'HEAD',
    'PATCH',
    'POST',
    'PUT',
)


PatOrStr: ta.TypeAlias = re.Pattern | str


log = logs.get_module_logger(globals())


##


@dc.dataclass(frozen=True)
class Route(lang.Final):
    method: str
    path: PatOrStr

    def __post_init__(self) -> None:
        check.non_empty_str(self.method)
        check.equal(self.method, self.method.upper())
        if isinstance(self.path, str):
            check.arg(self.path.startswith('/'))
        else:
            check.isinstance(self.path, re.Pattern)

    #

    @classmethod
    def delete(cls, path: PatOrStr) -> 'Route':
        return cls('DELETE', path)

    @classmethod
    def get(cls, path: PatOrStr) -> 'Route':
        return cls('GET', path)

    @classmethod
    def head(cls, path: PatOrStr) -> 'Route':
        return cls('HEAD', path)

    @classmethod
    def patch(cls, path: PatOrStr) -> 'Route':
        return cls('PATCH', path)

    @classmethod
    def post(cls, path: PatOrStr) -> 'Route':
        return cls('POST', path)

    @classmethod
    def put(cls, path: PatOrStr) -> 'Route':
        return cls('PUT', path)


class RouteHandler(ta.NamedTuple):
    route: Route
    handler: asgi.App


##


@dc.dataclass(frozen=True)
class _HandlesAppMarker(AppMarker, lang.Final):
    routes: ta.Sequence[Route]


@ta.overload
def handles(method: KnownMethod, path: PatOrStr) -> ta.Callable[[CallableT], CallableT]:
    ...


@ta.overload
def handles(*routes: Route) -> ta.Callable[[CallableT], CallableT]:
    ...


def handles(*args):
    routes: list[Route]
    if any(isinstance(a, Route) for a in args):
        routes = [check.isinstance(a, Route) for a in args]
    elif args:
        method, path = args
        routes = [Route(check.in_(method, KNOWN_METHODS), path)]
    else:
        routes = []

    def inner(fn):
        append_app_marker(fn, _HandlesAppMarker(routes))
        return fn

    return inner


HANDLES_APP_MARKER_PROCESSORS: AppMarkerProcessorMap = {
    _HandlesAppMarker: NopAppMarkerProcessor(),
}


##


class RouteHandlerHolder(lang.Abstract):
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


##


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


class RouteHandlerApp(asgi.App_):
    def __init__(
            self,
            route_handlers: ta.Mapping[Route, asgi.App],
            base_server_url: BaseServerUrl | None = None,
    ) -> None:
        super().__init__()

        self._route_handlers = route_handlers
        self._base_server_url = base_server_url

        pat_dct: dict[str, list[tuple[Route, asgi.App]]] = {}
        for r, a in route_handlers.items():
            if not isinstance(r.path, re.Pattern):
                continue
            pat_dct.setdefault(r.method, []).append((r, a))
        self._pat_route_handlers_by_method = pat_dct

    def _get_route_app(self, *, method: str, path: str) -> asgi.App | None:
        try:
            return self._route_handlers[Route(method, path)]
        except KeyError:
            pass

        if (pat_rts := self._pat_route_handlers_by_method.get(method)) is not None:
            pat_apps = [
                a
                for r, a in pat_rts
                if check.isinstance(r.path, re.Pattern).fullmatch(path)
            ]
            if pat_apps:
                return check.single(pat_apps)

        return None

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
                    if self._base_server_url is not None:
                        bsu = self._base_server_url
                    else:
                        sch = scope['scheme']
                        h, p = scope['server']
                        if (sch, p) not in self.URL_SCHEME_PORT_PAIRS:
                            ps = f':{p}'
                        else:
                            ps = ''
                        bsu = BaseServerUrl(f'{sch}://{h}{ps}/')
                    es.enter_context(lang.context_var_setting(BASE_SERVER_URL, bsu))  # noqa

                    app = self._get_route_app(
                        method=scope['method'],
                        path=scope['raw_path'].decode(),
                    )

                    if app is not None:
                        await app(scope, recv, send)

                    else:
                        await asgi.send_response(send, 404)

                case _:
                    raise ValueError(f'Unhandled scope type: {scope_ty!r}')
