import typing as ta

from omlish import check

from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import ToolExecResultMessage
from ...chat.messages import UserMessage


##


ROLES_MAP: ta.Mapping[type[Message], str] = {
    SystemMessage: 'system',
    UserMessage: 'user',
    AiMessage: 'assistant',
    ToolExecResultMessage: 'tool',
}


def get_msg_content(m: Message) -> str | None:
    if isinstance(m, (SystemMessage, AiMessage)):
        return m.s

    elif isinstance(m, UserMessage):
        return check.isinstance(m.c, str)

    else:
        raise TypeError(m)
