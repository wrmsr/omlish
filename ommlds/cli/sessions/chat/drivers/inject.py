"""
TODO:
 - private + expose(ChatDriver)
"""
import uuid

from omlish import inject as inj
from omlish import lang

from ....backends.types import DefaultBackendName
from .configs import DEFAULT_BACKEND
from .configs import DriverConfig


with lang.auto_proxy_import(globals()):
    from ....backends import inject as _backends
    from . import impl as _impl
    from . import types as _types
    from .ai import inject as _ai
    from .events import inject as _events
    from .phases import inject as _phases
    from .state import inject as _state
    from .tools import inject as _tools
    from .user import inject as _user


##


def bind_driver(cfg: DriverConfig = DriverConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _backends.bind_backends(cfg.backend),

        _ai.bind_ai(cfg.ai),

        _events.bind_events(),

        _phases.bind_phases(),

        _state.bind_state(cfg.state),

        _tools.bind_tools(cfg.tools),

        _user.bind_user(cfg.user),
    ])

    #

    els.extend([
        inj.bind(_impl.ChatDriverImpl, singleton=True),
        inj.bind(_types.ChatDriver, to_key=_impl.ChatDriverImpl),

        inj.bind_async_late(_types.ChatDriver, _types.ChatDriverGetter),
    ])

    #

    els.append(inj.bind(DefaultBackendName, to_const=DEFAULT_BACKEND))

    #

    els.append(inj.bind(_types.ChatDriverId(uuid.uuid4())))

    #

    return inj.as_elements(*els)
