import typing as ta

from omlish import dataclasses as dc
from omlish import inject as inj

from .base import Session
from .chat import ChatOption
from .chat import ChatOptions


##


@dc.dataclass(frozen=True, eq=False)
class InjectedChatOptions:
    v: ChatOptions


def bind_chat_options(*cos: ChatOption) -> inj.Elements:
    ico = InjectedChatOptions(ChatOptions(cos))
    ico_k: inj.Key = inj.Key(InjectedChatOptions, tag=inj.Id(id(ico)))

    return inj.as_elements(
        inj.bind(ico_k, to_const=ico),
        inj.set_binder[InjectedChatOptions]().bind(ico_k),
    )


def provide_chat_options(icos: ta.AbstractSet[InjectedChatOptions]) -> ChatOptions:
    return ChatOptions([
        co
        for ico in icos
        for co in ico.v
    ])


##


def bind_sessions(session_cfg: Session.Config) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(session_cfg),
        inj.bind(session_cfg.configurable_cls, singleton=True),
        inj.bind(Session, to_key=session_cfg.configurable_cls),
    ]

    #

    els.extend([
        inj.set_binder[InjectedChatOptions](),
        inj.bind(provide_chat_options, singleton=True),
    ])

    #

    return inj.as_elements(*els)
