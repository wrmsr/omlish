from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import UserChat
from ..types import Event


##


@dc.dataclass(frozen=True)
class UserMessagesEvent(Event, lang.Final):
    chat: UserChat
