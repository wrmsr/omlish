import typing as ta

from omlish import inject as inj
from omlish.http import asgi
from omlish.http import sessions

from .base import SCOPE
from .markers import AppMarker
from .markers import AppMarkerProcessor
from .markers import NopAppMarkerProcessor
from .routes import Route
from .routes import RouteHandlerHolder
from .routes import _HandlesAppMarker
from .routes import build_route_handler_map
from .sessions import SESSION
from .sessions import _WithSessionAppMarker
from .sessions import _WithSessionAppMarkerProcessor
from .templates import JinjaNamespace
from .templates import JinjaTemplates


##


def bind_route_handler_class(hc: type[RouteHandlerHolder]) -> inj.Elemental:
    return inj.as_elements(
        inj.bind(hc, singleton=True),
        inj.set_binder[RouteHandlerHolder]().bind(hc),
    )


def bind_app_marker_processor(mc: type[AppMarker], pc: type[AppMarkerProcessor]) -> inj.Elemental:
    return inj.as_elements(
        inj.bind(pc),
        inj.map_binder[type[AppMarker], AppMarkerProcessor]().bind(mc, pc),
    )


def _build_route_handler_map(
        handler_holders: ta.AbstractSet[RouteHandlerHolder],
        processors: ta.Mapping[type[AppMarker], AppMarkerProcessor],
) -> ta.Mapping[Route, asgi.App]:
    return build_route_handler_map(
        handler_holders,
        processors,
    )


def bind_route_handler_map() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(_build_route_handler_map, singleton=True),
        inj.map_binder[type[AppMarker], AppMarkerProcessor](),
    )


def bind() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(ta.Callable[[], asgi.Scope], to_const=SCOPE.get),
        inj.bind(ta.Callable[[], sessions.Session], to_const=SESSION.get),

        ##

        inj.map_binder[type[AppMarker], AppMarkerProcessor](),

        bind_app_marker_processor(_WithSessionAppMarker, _WithSessionAppMarkerProcessor),
        bind_app_marker_processor(_HandlesAppMarker, NopAppMarkerProcessor),

        ##

        inj.set_binder[RouteHandlerHolder](),
    )


def _build_jinja_namespaces(ns: ta.Annotated[ta.Mapping[str, ta.Any], inj.Tag(JinjaNamespace)]) -> JinjaNamespace:
    return JinjaNamespace(ns)


def bind_templates() -> inj.Elemental:
    return inj.as_elements(
        inj.bind(JinjaTemplates, singleton=True),

        inj.map_binder[str, ta.Any](tag=JinjaNamespace),
        inj.bind(_build_jinja_namespaces),
    )
