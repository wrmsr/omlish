import typing as ta

from omlish import check

from .....backends.google.protocol import types as pt
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage


##


ROLES_MAP: ta.Mapping[type[Message], pt.ContentRole | None] = {  # noqa
    SystemMessage: None,
    UserMessage: 'user',
    AiMessage: 'model',
    ToolUseMessage: 'model',
}


def make_str_content(
        s: str | None,
        *,
        role: pt.ContentRole | None = None,
) -> pt.Content | None:
    if s is None:
        return None

    return pt.Content(
        parts=[pt.Part(
            text=check.not_none(s),
        )],
        role=role,
    )


def make_msg_content(m: Message) -> pt.Content:
    if isinstance(m, (AiMessage, SystemMessage, UserMessage)):
        return check.not_none(make_str_content(
            check.isinstance(m.c, str),
            role=ROLES_MAP[type(m)],
        ))

    elif isinstance(m, ToolUseResultMessage):
        tr_resp_val: pt.Value
        if m.tur.c is None:
            tr_resp_val = pt.NullValue()  # type: ignore[unreachable]
        elif isinstance(m.tur.c, str):
            tr_resp_val = pt.StringValue(m.tur.c)
        else:
            raise TypeError(m.tur.c)

        return pt.Content(
            parts=[pt.Part(
                function_response=pt.FunctionResponse(
                    id=m.tur.id,
                    name=m.tur.name,
                    response={
                        'value': tr_resp_val,
                    },
                ),
            )],
        )

    elif isinstance(m, ToolUseMessage):
        return pt.Content(
            parts=[pt.Part(
                function_call=pt.FunctionCall(
                    id=m.tu.id,
                    name=m.tu.name,
                    args=m.tu.args,
                ),
            )],
            role='model',
        )

    else:
        raise TypeError(m)


def pop_system_instructions(msgs: list[Message]) -> pt.Content | None:
    if not msgs:
        return None

    m0 = msgs[0]
    if not isinstance(m0 := msgs[0], SystemMessage):
        return None

    msgs.pop(0)
    return make_msg_content(m0)


def get_msg_content(m: Message) -> str | None:
    if isinstance(m, AiMessage):
        return check.isinstance(m.c, str)

    elif isinstance(m, (SystemMessage, UserMessage)):
        return check.isinstance(m.c, str)

    else:
        raise TypeError(m)
