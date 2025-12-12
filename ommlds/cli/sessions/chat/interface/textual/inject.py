from omlish import inject as inj

from ..base import ChatInterface
from .app import ChatApp
from .interface import TextualChatInterface


##


def bind_textual() -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(ChatInterface, to_ctor=TextualChatInterface, singleton=True),
    ]

    els.extend([
        inj.bind(ChatApp, singleton=True),
    ])

    return inj.as_elements(*els)
