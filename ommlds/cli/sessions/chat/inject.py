from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang

from ..base import Session
from .configs import DEFAULT_CHAT_MODEL_BACKEND
from .configs import ChatConfig


with lang.auto_proxy_import(globals()):
    from . import driver as _driver
    from . import session as _session
    from .backends import inject as _backends
    from .chat.ai import inject as _chat_ai
    from .chat.state import inject as _chat_state
    from .chat.user import inject as _chat_user
    from .phases import inject as _phases
    from .rendering import inject as _rendering
    from .tools import inject as _tools


##


def bind_chat(cfg: ChatConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _backends.bind_backends(
            backend=cfg.backend or DEFAULT_CHAT_MODEL_BACKEND,
        ),

        _chat_ai.bind_ai(
            stream=cfg.stream,
            silent=cfg.silent,
            enable_tools=cfg.enable_tools,
        ),

        _chat_user.bind_user(
            initial_system_content=cfg.initial_system_content,
            initial_user_content=cfg.initial_user_content,
            interactive=cfg.interactive,
            use_readline=cfg.use_readline,
        ),

        _chat_state.bind_state(
            state=cfg.state,
        ),

        _phases.bind_phases(),

        _rendering.bind_rendering(
            markdown=cfg.markdown,
        ),
    ])

    #

    if cfg.enable_tools:
        els.append(_tools.bind_tools(
            silent=cfg.silent,
            dangerous_no_confirmation=cfg.dangerous_no_tool_confirmation,
            enabled_tools=cfg.enabled_tools,
        ))

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

    return inj.as_elements(*els)
