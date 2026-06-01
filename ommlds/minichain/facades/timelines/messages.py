import uuid

from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import ToolUseMessage
from ...chat.messages import UserMessage
from ...chat.metadata import MessageUuid
from .items import AiMessageTimelineItem
from .items import MessageTimelineItem
from .items import TimelineItem
from .items import TimelineItemId
from .items import ToolUseTimelineItem
from .items import ToolUseTimelineItemState
from .items import UserMessageTimelineItem


##


def timeline_item_id_from_message(message: Message) -> TimelineItemId:
    try:
        return TimelineItemId(message.metadata[MessageUuid].v)
    except KeyError:
        return TimelineItemId(uuid.uuid7())


def timeline_item_from_message(message: Message) -> TimelineItem:
    item_id = timeline_item_id_from_message(message)

    if isinstance(message, UserMessage):
        return UserMessageTimelineItem(
            id=item_id,
            message=message,
            finalized=True,
        )

    elif isinstance(message, AiMessage):
        return AiMessageTimelineItem(
            id=item_id,
            message=message,
            finalized=True,
        )

    elif isinstance(message, ToolUseMessage):
        return ToolUseTimelineItem(
            id=item_id,
            use=message.tu,
            state=ToolUseTimelineItemState.COMPLETE,
            finalized=True,
        )

    else:
        return MessageTimelineItem(
            id=item_id,
            message=message,
            finalized=True,
        )
