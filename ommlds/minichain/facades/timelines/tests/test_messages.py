import uuid

from ....chat.messages import AiMessage
from ....chat.messages import UserMessage
from ....chat.metadata import MessageUuid
from ...timelines.items import AiMessageTimelineItem
from ...timelines.items import UserMessageTimelineItem
from ...timelines.messages import timeline_item_from_message


def test_timeline_item_from_message_uses_message_uuid() -> None:
    message_uuid = uuid.uuid7()
    message = UserMessage('hi').with_metadata(MessageUuid(message_uuid))

    item = timeline_item_from_message(message)

    assert isinstance(item, UserMessageTimelineItem)
    assert item.id == message_uuid
    assert item.message is message
    assert item.finalized


def test_timeline_item_from_ai_message() -> None:
    message = AiMessage('hi')

    item = timeline_item_from_message(message)

    assert isinstance(item, AiMessageTimelineItem)
    assert item.message is message
    assert item.finalized
