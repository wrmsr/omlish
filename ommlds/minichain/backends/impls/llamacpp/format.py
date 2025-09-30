import typing as ta

from omlish import check

from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage


##


ROLES_MAP: ta.Mapping[type[Message], str] = {
    SystemMessage: 'system',
    UserMessage: 'user',
    AiMessage: 'assistant',
    ToolUseMessage: 'assistant',
    ToolUseResultMessage: 'tool',
}


def get_msg_content(m: Message) -> str | None:
    if isinstance(m, AiMessage):
        return check.isinstance(m.c, (str, None))

    elif isinstance(m, (SystemMessage, UserMessage)):
        return check.isinstance(m.c, str)

    else:
        raise TypeError(m)
