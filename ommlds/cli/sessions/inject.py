from omlish import inject as inj

from .base import Session
from .chat.base import ChatSession
from .chat2.session import Chat2Session


##


def bind_sessions(session_cfg: Session.Config) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(session_cfg),
        inj.bind(session_cfg.configurable_cls, singleton=True),
        inj.bind(Session, to_key=session_cfg.configurable_cls),
    ]

    if isinstance(session_cfg, ChatSession.Config):
        from .chat.inject import bind_chat_session
        els.append(bind_chat_session(session_cfg))

    elif isinstance(session_cfg, Chat2Session.Config):
        from .chat2.inject import bind_chat
        els.append(bind_chat(session_cfg))  # noqa

    return inj.as_elements(*els)
