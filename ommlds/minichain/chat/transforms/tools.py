import typing as ta
import uuid

from omlish import dataclasses as dc

from ..messages import AiMessage
from ..messages import Message
from ..messages import ToolExecRequest
from .base import MessageTransform


##


@dc.dataclass(frozen=True)
class ToolExecRequestIdAddingMessageTransform(MessageTransform):
    id_factory: ta.Callable[[AiMessage, ToolExecRequest], str] = dc.field(default=lambda m, ter: str(uuid.uuid4()))

    def transform_message(self, m: Message) -> Message:
        if not isinstance(m, AiMessage) or not m.tool_exec_requests:
            return m

        lst: list[ToolExecRequest] = []
        for ter in m.tool_exec_requests:
            if ter.id is None:
                ter = dc.replace(ter, id=self.id_factory(m, ter))
            lst.append(ter)

        return dc.replace(m, tool_exec_requests=lst)
