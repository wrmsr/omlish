import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish.formats import json

from .....backends.anthropic.protocol import types as pt
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.tools.types import Tool
from ....content.prepare import prepare_content_str
from ....tools.jsonschema import build_tool_spec_params_json_schema


##


def get_message_content(m: Message) -> str | None:
    if isinstance(m, AiMessage):
        return check.isinstance(m.c, str)

    elif isinstance(m, (UserMessage, SystemMessage)):
        return check.isinstance(m.c, str)

    else:
        raise TypeError(m)


#


class BuiltChatMessages(ta.NamedTuple):
    messages: list[pt.Message]
    system: list[pt.Content] | None


ROLES_MAP: ta.Mapping[type[Message], str] = {
    SystemMessage: 'system',
    UserMessage: 'user',
    AiMessage: 'assistant',
    ToolUseMessage: 'assistant',
}


def build_protocol_chat_messages(msgs: ta.Iterable[Message]) -> BuiltChatMessages:
    messages: list[pt.Message] = []
    system: list[pt.Content] | None = None

    for i, m in enumerate(msgs):
        if isinstance(m, SystemMessage):
            if i or system is not None:
                raise Exception('Only supports one system message and must be first')
            system = [pt.Text(check.not_none(get_message_content(m)))]

        elif isinstance(m, ToolUseResultMessage):
            messages.append(pt.Message(
                role='user',
                content=[pt.ToolResult(
                    tool_use_id=check.not_none(m.tur.id),
                    content=json.dumps_compact(msh.marshal(m.tur.c)) if not isinstance(m.tur.c, str) else m.tur.c,
                )],
            ))

        elif isinstance(m, AiMessage):
            # messages.append(pt.Message(
            #     role=ROLES_MAP[type(m)],  # noqa
            #     content=[pt.Text(check.isinstance(get_message_content(m), str))],
            # ))
            messages.append(pt.Message(
                role='assistant',
                content=[
                    *([pt.Text(check.isinstance(m.c, str))] if m.c is not None else []),
                ],
            ))

        elif isinstance(m, ToolUseMessage):
            messages.append(pt.Message(
                role='assistant',
                content=[
                    pt.ToolUse(
                        id=check.not_none(m.tu.id),
                        name=check.not_none(m.tu.name),
                        input=m.tu.args,
                    ),
                ],
            ))

        else:
            messages.append(pt.Message(
                role=ROLES_MAP[type(m)],  # type: ignore[arg-type]
                content=[pt.Text(check.isinstance(get_message_content(m), str))],
            ))

    return BuiltChatMessages(messages, system)


##


def build_protocol_tool(t: Tool) -> pt.ToolSpec:
    return pt.ToolSpec(
        name=check.not_none(t.spec.name),
        description=prepare_content_str(t.spec.desc),
        input_schema=build_tool_spec_params_json_schema(t.spec),
    )
