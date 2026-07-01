import dataclasses as dc
import typing as ta

from ..typetags import TypeTagged
from ..tools import ToolCall
from ..responses import Usage


##


class ResponseMessage(
    TypeTagged,
    type_tag_field='role',
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantResponseMessage[
    ToolCallT: ToolCall = ToolCall,
](
    ResponseMessage,
    type_tag='assistant',
):
    content: str | None = None
    tool_calls: ta.Sequence[ToolCallT] | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class Choice[
    ResponseMessageT: ResponseMessage = ResponseMessage,
    FinishReasonT: str = str,
]:
    index: int
    message: ResponseMessageT
    finish_reason: FinishReasonT | None


##


@dc.dataclass(frozen=True, kw_only=True)
class Response[
    ChoiceT: Choice = Choice,
    UsageT: Usage = Usage,
](
    TypeTagged,
    type_tag_field='object',
    type_tag='chat.completion',
):
    id: str
    created: int
    model: str
    choices: ta.Sequence[ChoiceT]
    usage: UsageT | None = None
