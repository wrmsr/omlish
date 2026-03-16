import uuid

from omlish import dataclasses as dc
from omlish import lang

from ..chat.messages import UserChat
from .types import Action


##


@dc.dataclass(frozen=True)
class SendUserMessagesAction(Action, lang.Final):
    next_user_chat: UserChat

    _: dc.KW_ONLY

    ai_message_uuid: uuid.UUID | None = None
