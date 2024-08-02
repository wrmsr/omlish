from omlish import inject as inj

from .login import _LoginRequiredAppMarker
from .login import _LoginRequiredAppMarkerProcessor
from .markers import AppMarker
from .markers import AppMarkerProcessor
from .markers import NopAppMarkerProcessor
from .routes import _HandlesAppMarker
from .sessions import _WithSessionAppMarker
from .sessions import _WithSessionAppMarkerProcessor
from .users import _WithUserAppMarker
from .users import _WithUserAppMarkerProcessor


def bind_app_marker_processor(mc: type[AppMarker], pc: type[AppMarkerProcessor]) -> inj.Elemental:
    return inj.as_elements(
        inj.bind(pc),
        inj.map_binder[type[AppMarker], AppMarkerProcessor]().bind(mc, pc),
    )


def bind() -> inj.Elemental:
    return inj.as_elements(
        bind_app_marker_processor(_WithSessionAppMarker, _WithSessionAppMarkerProcessor),
        bind_app_marker_processor(_WithUserAppMarker, _WithUserAppMarkerProcessor),
        bind_app_marker_processor(_LoginRequiredAppMarker, _LoginRequiredAppMarkerProcessor),
        bind_app_marker_processor(_HandlesAppMarker, NopAppMarkerProcessor),
    )
