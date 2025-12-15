from omlish import inject as inj

from ...chat.user.types import UserChatInput
from ..base import ChatInterface
from .app import ChatApp
from .interface import TextualChatInterface
from .user import QueueUserChatInput


##


def bind_textual() -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(ChatInterface, to_ctor=TextualChatInterface, singleton=True),
    ]

    els.extend([
        inj.bind(ChatApp, singleton=True),
    ])

    els.extend([
        inj.bind(QueueUserChatInput, singleton=True),
        inj.bind(UserChatInput, to_key=QueueUserChatInput),
    ])

    return inj.as_elements(*els)
