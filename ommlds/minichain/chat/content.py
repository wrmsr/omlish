import typing as ta

from ..content.content import Content
from ..content.transform.strings import transform_content_strings
from .messages import AiMessage
from .messages import Message
from .messages import SystemMessage
from .messages import ToolUseMessage
from .messages import ToolUseResultMessage
from .messages import UserMessage


MessageT = ta.TypeVar('MessageT', bound=Message)


##


def transform_message_content(fn: ta.Callable[[Content], Content], m: MessageT) -> MessageT:
    if isinstance(m, UserMessage):
        return m.replace(c=fn(m.c))

    elif isinstance(m, AiMessage):
        return m.replace(c=fn(m.c))

    elif isinstance(m, SystemMessage):
        return m.replace(c=fn(m.c))

    elif isinstance(m, ToolUseMessage):
        # TODO: m.tu.args?
        return m

    elif isinstance(m, ToolUseResultMessage):
        # TODO: m.tur.c?
        return m

    else:
        raise TypeError(m)


def transform_message_content_strings(fn: ta.Callable[[str], str], m: MessageT) -> MessageT:
    return transform_message_content(lambda c: transform_content_strings(fn, c), m)
