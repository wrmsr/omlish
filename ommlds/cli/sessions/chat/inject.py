import typing as ta

from omlish import dataclasses as dc
from omlish import inject as inj

from .base import ChatOption
from .base import ChatOptions
from .base import ChatSession
from .state import ChatStateManager
from .state import StateStorageChatStateManager


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


def bind_chat_session(cfg: ChatSession.Config) -> inj.Elements:
    els: list[inj.Elemental] = []

    els.extend([
        inj.set_binder[InjectedChatOptions](),
        inj.bind(provide_chat_options, singleton=True),
    ])

    els.extend([
        inj.bind(StateStorageChatStateManager, singleton=True),
        inj.bind(ChatStateManager, to_key=StateStorageChatStateManager),
    ])

    return inj.as_elements(*els)
