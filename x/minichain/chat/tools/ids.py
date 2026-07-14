import typing as ta
import uuid

from omcore import dataclasses as dc

from ..messages import Chat
from ..messages import Message
from ..messages import ToolUseMessage
from ..transform.types import MessageTransform


##


def simple_uuid_tool_exec_request_id_factory(m: ToolUseMessage) -> str:  # noqa
    return str(uuid.uuid7())


@dc.dataclass(frozen=True)
class ToolUseIdAddingMessageTransform(MessageTransform):
    id_factory: ta.Callable[[ToolUseMessage], str] = dc.field(default=simple_uuid_tool_exec_request_id_factory)  # noqa

    def transform(self, m: Message) -> Chat:
        if not isinstance(m, ToolUseMessage) or m.tu.id is not None:
            return [m]

        return [dc.replace(m, tu=dc.replace(m.tu, id=self.id_factory(m)))]
