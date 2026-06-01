import enum
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import UserMessage
from ...content.content import Content
from ...tools.execution.execution import ToolUseExecution
from ...tools.types import ToolUse
from ...tools.types import ToolUseResult


TimelineId = ta.NewType('TimelineId', uuid.UUID)
TimelineItemId = ta.NewType('TimelineItemId', uuid.UUID)


##


class ToolUseTimelineItemState(enum.StrEnum):
    RUNNING = 'running'
    COMPLETE = 'complete'
    DENIED = 'denied'
    FAILED = 'failed'


##


@dc.dataclass(frozen=True, kw_only=True)
@msh.set_polymorphic_from_subclasses(naming=msh.Naming.SNAKE, strip_suffix=True)
class TimelineItem(lang.Abstract, lang.Sealed):
    id: TimelineItemId = dc.field(default_factory=lambda: TimelineItemId(uuid.uuid7()))
    revision: int = 0
    finalized: bool = False


@dc.dataclass(frozen=True, kw_only=True)
class UserMessageTimelineItem(TimelineItem, lang.Final):
    message: UserMessage


@dc.dataclass(frozen=True, kw_only=True)
class AiMessageTimelineItem(TimelineItem, lang.Final):
    message: AiMessage


@dc.dataclass(frozen=True, kw_only=True)
class AiStreamTimelineItem(TimelineItem, lang.Final):
    message_uuid: uuid.UUID
    content: Content | None = None
    error: BaseException | lang.OpaqueRepr | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options('execution', no_marshal=True, no_unmarshal=True)
@msh.update_field_options(
    'error',
    marshal_via=msh.MarshalVia(lang.OpaqueRepr | None),
    unmarshal_via=msh.UnmarshalVia(lang.OpaqueRepr | None),
)
class ToolUseTimelineItem(TimelineItem, lang.Final):
    use: ToolUse
    state: ToolUseTimelineItemState

    result: ToolUseResult | None = None
    execution: ToolUseExecution | None = None
    error: BaseException | lang.OpaqueRepr | None = None


@dc.dataclass(frozen=True, kw_only=True)
class MessageTimelineItem(TimelineItem, lang.Final):
    message: Message


@dc.dataclass(frozen=True, kw_only=True)
class UiMessageTimelineItem(TimelineItem, lang.Final):
    content: Content
