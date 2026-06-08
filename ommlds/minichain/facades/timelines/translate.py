"""
Translation of persisted/canonical messages into timeline items - the replay half of the convergence invariant: a chat
loaded from storage must translate into the same item sequence (ids, types, payloads) a live watcher of that
conversation ended up with.

Identity: items derive their ids from message `MessageUuid`s wherever present (matching what the live manager builds).
Tool use/result pairing is *chat-sequence-aware*: `ToolUseResultMessage`s fold into their use's item (paired by tool
call id), anchored at the use's position - they do not become separate items, just as they don't live.
"""
import typing as ta
import uuid

from omlish import dataclasses as dc

from ...chat.messages import AiMessage
from ...chat.messages import Chat
from ...chat.messages import Message
from ...chat.messages import ThinkingMessage
from ...chat.messages import ToolUseMessage
from ...chat.messages import ToolUseResultMessage
from ...chat.messages import UserMessage
from ...chat.metadata import MessageUuid
from .items import AiMessageTimelineItem
from .items import MessageTimelineItem
from .items import ThinkingTimelineItem
from .items import TimelineItem
from .items import TimelineItemId
from .items import ToolUseTimelineItem
from .items import ToolUseTimelineItemState
from .items import UserMessageTimelineItem


T = ta.TypeVar('T')


##


def timeline_item_id_for_message(message: Message) -> TimelineItemId:
    if (mu := message.metadata.get(MessageUuid)) is not None:
        return TimelineItemId(mu.v)

    return TimelineItemId(uuid.uuid7())


def timeline_translate_message(message: Message) -> TimelineItem:
    """
    Translates a single canonical message, without tool result pairing - a `ToolUseMessage` becomes a PENDING
    (unfinalized) tool item, and a `ToolUseResultMessage` an orphan-result one. Prefer `translate_chat` (or anchored
    translation) when a whole chat sequence is in hand.
    """

    item_id = timeline_item_id_for_message(message)

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

    elif isinstance(message, ThinkingMessage):
        return ThinkingTimelineItem(
            id=item_id,
            message=message,
            finalized=True,
        )

    elif isinstance(message, ToolUseMessage):
        return ToolUseTimelineItem(
            id=item_id,
            state=ToolUseTimelineItemState.PENDING,
            use=message.tu,
        )

    elif isinstance(message, ToolUseResultMessage):
        return ToolUseTimelineItem(
            id=item_id,
            state=ToolUseTimelineItemState.COMPLETE,
            result=message.tur,
            finalized=True,
        )

    else:
        return MessageTimelineItem(
            id=item_id,
            message=message,
            finalized=True,
        )


##


@dc.dataclass(frozen=True)
class AnchoredTimelineItem(ta.Generic[T]):
    """A translated item anchored to its primary message's source key (e.g. a storage seq)."""

    anchor: T
    item: TimelineItem


def timeline_translate_anchored_chat(rows: ta.Iterable[tuple[T, Message]]) -> list[AnchoredTimelineItem[T]]:
    """
    Translates a contiguous chat slice, pairing tool results into their uses' items (anchored at the *use*). A
    `ToolUseResultMessage` whose use lies outside the slice becomes an orphan-result tool item at its own anchor; a
    `ToolUseMessage` whose result lies outside the slice yields an unfinalized PENDING item - both shapes heal when a
    slice containing the pair is translated instead.
    """

    row_lst = list(rows)

    # Each tool result pairs to the nearest preceding unconsumed use with a matching call id. Pairing is by list
    # position (not message identity or uuid) so it is insensitive to missing metadata.
    paired_result_idxs_by_use_idx: dict[int, int] = {}
    paired_result_idxs: set[int] = set()
    open_use_idxs_by_key: dict[str, list[int]] = {}

    for i, (_, m) in enumerate(row_lst):
        if isinstance(m, ToolUseMessage):
            open_use_idxs_by_key.setdefault(m.tu.id or m.tu.name, []).append(i)

        elif isinstance(m, ToolUseResultMessage):
            if (use_idxs := open_use_idxs_by_key.get(m.tur.id or m.tur.name)):
                use_idx = use_idxs.pop(0)
                paired_result_idxs_by_use_idx[use_idx] = i
                paired_result_idxs.add(i)

    out: list[AnchoredTimelineItem[T]] = []

    for i, (anchor, m) in enumerate(row_lst):
        if isinstance(m, ToolUseMessage):
            item = ToolUseTimelineItem(
                id=timeline_item_id_for_message(m),
                state=ToolUseTimelineItemState.PENDING,
                use=m.tu,
            )

            if (result_idx := paired_result_idxs_by_use_idx.get(i)) is not None:
                turm = ta.cast(ToolUseResultMessage, row_lst[result_idx][1])
                item = dc.replace(
                    item,
                    state=ToolUseTimelineItemState.COMPLETE,
                    result=turm.tur,
                    finalized=True,
                )

            out.append(AnchoredTimelineItem(anchor, item))

        elif isinstance(m, ToolUseResultMessage):
            if i in paired_result_idxs:
                continue

            out.append(AnchoredTimelineItem(anchor, timeline_translate_message(m)))

        else:
            out.append(AnchoredTimelineItem(anchor, timeline_translate_message(m)))

    return out


def timeline_translate_chat(chat: Chat) -> list[TimelineItem]:
    return [at.item for at in timeline_translate_anchored_chat(enumerate(chat))]
