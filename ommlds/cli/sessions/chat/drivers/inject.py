from omlish import inject as inj
from omlish import lang

from ....backends.types import DefaultBackendName
from .configs import DEFAULT_BACKEND
from .configs import DriverConfig


with lang.auto_proxy_import(globals()):
    from ....backends import inject as _backends
    from . import driver as _driver
    from .chat.ai import inject as _chat_ai
    from .chat.state import inject as _chat_state
    from .chat.user import inject as _chat_user
    from .phases import inject as _phases
    from .tools import inject as _tools


##


def bind_driver(cfg: DriverConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _backends.bind_backends(cfg.backend),

        _chat_ai.bind_ai(cfg.ai),

        _chat_user.bind_user(cfg.user),

        _chat_state.bind_state(cfg.state),

        _phases.bind_phases(),

        _tools.bind_tools(cfg.tools),
    ])

    #

    els.extend([
        inj.bind(_driver.ChatDriver, singleton=True),
    ])

    #

    els.append(inj.bind(DefaultBackendName, to_const=DEFAULT_BACKEND))

    #

    return inj.as_elements(*els)
