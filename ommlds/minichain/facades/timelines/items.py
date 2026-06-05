"""
The timeline item vocabulary: the domain-shaped, frontend-agnostic things a chat frontend displays, in order. Items are
frozen values identified by `id` and versioned by `revision`; `finalized` means an item will never change again.

Item identity is deliberately stable across live observation and later replay: wherever an item corresponds to a
message, its id is that message's `MessageUuid`. In-flight streaming items (`AiStreamTimelineItem`,
`ThinkingStreamTimelineItem`, tool items in the STREAMING state) are transient live-only shapes that are *replaced* -
same id, advanced revision - by their canonical message-derived forms when the stream's joined messages arrive. A
frontend that watched a conversation live and one that loads it later thus converge on identical item sequences (see
the package README for this convergence invariant).
"""
import enum
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import ThinkingMessage
from ...chat.messages import UserMessage
from ...content.content import Content
from ...tools.execution.execution import ToolUseExecution
from ...tools.types import ToolUse
from ...tools.types import ToolUseResult
from ...ui.text import UiText


TimelineId = ta.NewType('TimelineId', uuid.UUID)
TimelineItemId = ta.NewType('TimelineItemId', uuid.UUID)


##


@dc.dataclass(frozen=True, kw_only=True)
@msh.set_polymorphic_from_subclasses(naming=msh.Naming.SNAKE, strip_suffix=True)
class TimelineItem(lang.Abstract, lang.Sealed):
    id: TimelineItemId = dc.field(default_factory=lambda: TimelineItemId(uuid.uuid7()))
    revision: int = 0
    finalized: bool = False


##


@dc.dataclass(frozen=True, kw_only=True)
class UserMessageTimelineItem(TimelineItem, lang.Final):
    message: UserMessage


@dc.dataclass(frozen=True, kw_only=True)
class AiMessageTimelineItem(TimelineItem, lang.Final):
    message: AiMessage


@dc.dataclass(frozen=True, kw_only=True)
class ThinkingTimelineItem(TimelineItem, lang.Final):
    message: ThinkingMessage


@dc.dataclass(frozen=True, kw_only=True)
class MessageTimelineItem(TimelineItem, lang.Final):
    """The catch-all for message kinds without a dedicated item shape (system, developer, ...)."""

    message: Message


##
# In-flight streaming items. These exist only while watching live, and only until the stream's joined canonical
# messages arrive and replace them. A stream item that instead carries an `error` is terminal: there is no canonical
# form coming, and it is finalized as-is.


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options(
    'error',
    marshal_via=msh.MarshalVia(lang.OpaqueRepr | None),
    unmarshal_via=msh.UnmarshalVia(lang.OpaqueRepr | None),
)
class AiStreamTimelineItem(TimelineItem, lang.Final):
    message_uuid: uuid.UUID
    content: Content | None = None
    error: BaseException | lang.OpaqueRepr | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options(
    'error',
    marshal_via=msh.MarshalVia(lang.OpaqueRepr | None),
    unmarshal_via=msh.UnmarshalVia(lang.OpaqueRepr | None),
)
class ThinkingStreamTimelineItem(TimelineItem, lang.Final):
    message_uuid: uuid.UUID
    text: str = ''
    error: BaseException | lang.OpaqueRepr | None = None


##


class ToolUseTimelineItemState(enum.StrEnum):
    STREAMING = 'streaming'  # args are still streaming in (live-only)
    PENDING = 'pending'  # the use is fully known but execution has not (yet) been observed
    RUNNING = 'running'
    COMPLETE = 'complete'
    DENIED = 'denied'  # not yet observable - denials currently surface as COMPLETE results describing the denial
    FAILED = 'failed'  # not yet observable - failures currently surface as COMPLETE results describing the error


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options('execution', no_marshal=True, no_unmarshal=True)
@msh.update_field_options(
    'error',
    marshal_via=msh.MarshalVia(lang.OpaqueRepr | None),
    unmarshal_via=msh.UnmarshalVia(lang.OpaqueRepr | None),
)
class ToolUseTimelineItem(TimelineItem, lang.Final):
    """
    The unified tool card: one item follows a tool use through its whole lifecycle - optionally streaming in
    (`partial_*` fields accumulate while `use` is still None), then pending/running/completed with its result folded
    in. `execution` is a live-only object reference and does not marshal.
    """

    state: ToolUseTimelineItemState

    use: ToolUse | None = None

    partial_name: str | None = None
    partial_raw_args: str | None = None

    result: ToolUseResult | None = None
    error: BaseException | lang.OpaqueRepr | None = None

    execution: ToolUseExecution | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class UiMessageTimelineItem(TimelineItem, lang.Final):
    """A user-facing notice (not part of the model conversation) - UiText, never seen by the LLM."""

    text: UiText


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_field_options(
    'error',
    marshal_via=msh.MarshalVia(lang.OpaqueRepr | None),
    unmarshal_via=msh.UnmarshalVia(lang.OpaqueRepr | None),
)
class ErrorTimelineItem(TimelineItem, lang.Final):
    message: str | None = None
    error: BaseException | lang.OpaqueRepr | None = None
