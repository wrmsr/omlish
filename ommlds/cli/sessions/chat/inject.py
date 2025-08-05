import typing as ta

from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang

from ...backends.catalog import BackendCatalogEntry
from .backends import CHAT_BACKEND_CATALOG_ENTRIES
from .base import ChatOption
from .base import ChatOptions
from .base import ChatSession
from .printing import ChatSessionPrinter
from .printing import StringChatSessionPrinter
from .state import ChatStateManager
from .state import StateStorageChatStateManager


##


@dc.dataclass(frozen=True, eq=False)
class _InjectedChatOptions:
    v: ChatOptions


def bind_chat_options(*cos: ChatOption) -> inj.Elements:
    return inj.bind_set_entry_const(ta.AbstractSet[_InjectedChatOptions], _InjectedChatOptions(ChatOptions(cos)))


##


def bind_chat_session(cfg: ChatSession.Config) -> inj.Elements:
    els: list[inj.Elemental] = []

    els.extend([
        inj.set_binder[_InjectedChatOptions](),
        inj.bind(
            lang.typed_lambda(ChatOptions, s=ta.AbstractSet[_InjectedChatOptions])(
                lambda s: ChatOptions([
                    co
                    for ico in s
                    for co in ico.v
                ]),
            ),
            singleton=True,
        ),
    ])

    els.extend([
        inj.bind(StateStorageChatStateManager, singleton=True),
        inj.bind(ChatStateManager, to_key=StateStorageChatStateManager),
    ])

    els.extend([
        inj.bind(StringChatSessionPrinter, singleton=True),
        inj.bind(ChatSessionPrinter, to_key=StringChatSessionPrinter),
    ])

    els.extend([
        inj.bind_set_entry_const(ta.AbstractSet[BackendCatalogEntry], e)
        for e in CHAT_BACKEND_CATALOG_ENTRIES
    ])

    return inj.as_elements(*els)
