from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang

from ...backends.types import DefaultBackendName
from ..base import Session
from .configs import DEFAULT_BACKEND
from .configs import ChatConfig


with lang.auto_proxy_import(globals()):
    from ...backends import inject as _backends
    from ...rendering import inject as _rendering
    from . import driver as _driver
    from . import session as _session
    from .chat.ai import inject as _chat_ai
    from .chat.state import inject as _chat_state
    from .chat.user import inject as _chat_user
    from .phases import inject as _phases
    from .tools import inject as _tools


##


def bind_chat(cfg: ChatConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _backends.bind_backends(cfg.backend),

        _chat_ai.bind_ai(cfg.ai),

        _chat_user.bind_user(cfg.user),

        _chat_state.bind_state(cfg.state),

        _phases.bind_phases(),

        _rendering.bind_rendering(cfg.rendering),

        _tools.bind_tools(cfg.tools),
    ])

    #

    els.extend([
        inj.bind(_driver.ChatDriver, singleton=True),
    ])

    #

    els.extend([
        inj.bind(_session.ChatSession.Config(**dc.asdict(cfg))),
        inj.bind(Session, to_ctor=_session.ChatSession, singleton=True),
    ])

    #

    els.append(inj.bind(DefaultBackendName, to_const=DEFAULT_BACKEND))

    #

    return inj.as_elements(*els)
