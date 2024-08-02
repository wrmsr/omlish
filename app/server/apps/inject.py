import typing as ta

from omlish import inject as inj
from omlish.http import sessions
from omlish.http.asgi import AsgiApp
from omlish.http.asgi import AsgiScope

from ...users import User
from .base import SCOPE
from .login import _LoginRequiredAppMarker
from .login import _LoginRequiredAppMarkerProcessor
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
from .users import USER
from .users import _WithUserAppMarker
from .users import _WithUserAppMarkerProcessor


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
        inj.bind(ta.Callable[[], User | None], to_const=USER.get),

        ##

        inj.map_binder[type[AppMarker], AppMarkerProcessor](),

        bind_app_marker_processor(_WithSessionAppMarker, _WithSessionAppMarkerProcessor),
        bind_app_marker_processor(_WithUserAppMarker, _WithUserAppMarkerProcessor),
        bind_app_marker_processor(_LoginRequiredAppMarker, _LoginRequiredAppMarkerProcessor),
        bind_app_marker_processor(_HandlesAppMarker, NopAppMarkerProcessor),

        ##

        inj.set_binder[Handler_](),
    )
