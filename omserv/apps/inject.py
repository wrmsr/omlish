import typing as ta

from omlish import inject as inj
from omlish import lang
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiScope

from .base import SCOPE
from .markers import AppMarker
from .markers import AppMarkerProcessor
from .markers import NopAppMarkerProcessor
from .markers import get_app_markers
from .routes import Handler_
from .routes import Route
from .routes import _HandlesAppMarker
from .sessions import SESSION
from .sessions import _WithSessionAppMarker
from .sessions import _WithSessionAppMarkerProcessor
from .templates import J2Namespace
from .templates import J2Templates


def bind_handler(hc: type[Handler_]) -> inj.Elemental:
    return inj.as_elements(
        inj.bind(hc, singleton=True),
        inj.set_binder[Handler_]().bind(hc),
    )


def bind_app_marker_processor(mc: type[AppMarker], pc: type[AppMarkerProcessor]) -> inj.Elemental:
    return inj.as_elements(
        inj.bind(pc),
        inj.map_binder[type[AppMarker], AppMarkerProcessor]().bind(mc, pc),
    )


def _build_route_handler_map(
        handlers: ta.AbstractSet[Handler_],
        processors: ta.Mapping[type[AppMarker], AppMarkerProcessor],
) -> ta.Mapping[Route, AsgiApp]:
    route_handlers: dict[Route, AsgiApp] = {}
    for h in handlers:
        for rh in h.get_route_handlers():
            app = rh.handler
            markers = get_app_markers(rh.handler)
            for m in markers:
                mp = processors[type(m)]
                if mp is not None:
                    app = mp(app)
            route_handlers[rh.route] = app
    return route_handlers


def bind_route_handler_map() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(_build_route_handler_map, singleton=True),
        inj.map_binder[type[AppMarker], AppMarkerProcessor](),
    )


def bind() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(ta.Callable[[], AsgiScope], to_const=SCOPE.get),
        inj.bind(ta.Callable[[], sessions.Session], to_const=SESSION.get),

        ##

        inj.map_binder[type[AppMarker], AppMarkerProcessor](),

        bind_app_marker_processor(_WithSessionAppMarker, _WithSessionAppMarkerProcessor),
        bind_app_marker_processor(_HandlesAppMarker, NopAppMarkerProcessor),

        ##

        inj.set_binder[Handler_](),
    )


def _merge_j2_namespaces(nss: ta.AbstractSet[J2Namespace]) -> J2Namespace:
    return J2Namespace({k: v for ns in nss for k, v in ns.items()})


def bind_templates() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(J2Templates, singleton=True),

        inj.set_binder[J2Namespace](),
        inj.bind(_merge_j2_namespaces),
    )
