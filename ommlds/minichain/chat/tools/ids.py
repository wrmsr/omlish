import typing as ta
import uuid

from omlish import dataclasses as dc

from ..messages import AiMessage
from ..messages import Message
from ..messages import ToolExecRequest
from ..transforms.base import MessageTransform


##


def simple_uuid_tool_exec_request_id_factory(m: AiMessage, ter: ToolExecRequest) -> str:  # noqa
    return str(uuid.uuid4())


@dc.dataclass(frozen=True)
class ToolExecRequestIdAddingMessageTransform(MessageTransform):
    id_factory: ta.Callable[[AiMessage, ToolExecRequest], str] = dc.field(default=simple_uuid_tool_exec_request_id_factory)  # noqa

    def transform_message(self, m: Message) -> Message:
        if not isinstance(m, AiMessage) or not m.tool_exec_requests:
            return m

        lst: list[ToolExecRequest] = []
        for ter in m.tool_exec_requests:
            if ter.id is None:
                ter = dc.replace(ter, id=self.id_factory(m, ter))
            lst.append(ter)

        return dc.replace(m, tool_exec_requests=lst)
