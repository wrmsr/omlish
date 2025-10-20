from omlish import inject as inj

from .base import Session
from .chat.session import ChatSession


##


def bind_sessions(session_cfg: Session.Config) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(session_cfg),
        inj.bind(session_cfg.configurable_cls, singleton=True),
        inj.bind(Session, to_key=session_cfg.configurable_cls),
    ]

    if isinstance(session_cfg, ChatSession.Config):
        from .chat.inject import bind_chat
        els.append(bind_chat(session_cfg))  # noqa

    return inj.as_elements(*els)
