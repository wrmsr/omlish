import typing as ta

from omlish import inject as inj
from omserv.apps import inject as base_apps_inj

from ...users import User
from .login import _LoginRequiredAppMarker
from .login import _LoginRequiredAppMarkerProcessor
from .users import USER
from .users import _WithUserAppMarker
from .users import _WithUserAppMarkerProcessor


##


def bind() -> inj.Elemental:
    return inj.as_elements(
        base_apps_inj.bind(),
        base_apps_inj.bind_route_handler_map(),
        base_apps_inj.bind_templates(),

        ##

        inj.bind(ta.Callable[[], User | None], to_const=USER.get),

        ##

        base_apps_inj.bind_app_marker_processor(_WithUserAppMarker, _WithUserAppMarkerProcessor),
        base_apps_inj.bind_app_marker_processor(_LoginRequiredAppMarker, _LoginRequiredAppMarkerProcessor),
    )
