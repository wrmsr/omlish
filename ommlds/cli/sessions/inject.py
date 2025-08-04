from omlish import inject as inj

from .base import Session
from .chat.base import ChatSession
from .chat.inject import bind_chat_session


##


def bind_sessions(session_cfg: Session.Config) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(session_cfg),
        inj.bind(session_cfg.configurable_cls, singleton=True),
        inj.bind(Session, to_key=session_cfg.configurable_cls),
    ]

    if isinstance(session_cfg, ChatSession.Config):
        els.append(bind_chat_session(session_cfg))

    return inj.as_elements(*els)
