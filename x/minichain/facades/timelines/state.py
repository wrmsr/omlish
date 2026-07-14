"""
The live, in-memory state of a timeline: an append-ordered collection of items with O(1) id lookup, monotonic item
*positions*, and a monotonic event *watermark*. Mutations return the watermark-stamped events describing them; emission
is the caller's (the manager's) concern.

Positions are append-order ints and are never reused; storage is index-shifted by a base offset so that evicting old
finalized items (a designed-for future capability for long sessions) cannot disturb the position of anything else.

This class is not thread-safe and performs no synchronization: it is written to be owned by a single event loop, with
all mutation happening synchronously within event-callback dispatch. The attach coherence recipe (see the package
README) depends on reads being snapshots taken without intervening awaits.
"""
import typing as ta

from omcore import check

from ...content.content import Content
from .events import TimelineItemAppendedEvent
from .events import TimelineItemDeltaEvent
from .events import TimelineItemUpdatedEvent
from .items import TimelineId
from .items import TimelineItem
from .items import TimelineItemId


##


class TimelineState:
    def __init__(
            self,
            *,
            timeline_id: TimelineId,
    ) -> None:
        super().__init__()

        self._timeline_id = timeline_id

        self._items: list[TimelineItem] = []
        self._base_position = 0
        self._positions_by_id: dict[TimelineItemId, int] = {}

        self._watermark = 0

    @property
    def timeline_id(self) -> TimelineId:
        return self._timeline_id

    @property
    def watermark(self) -> int:
        return self._watermark

    def __len__(self) -> int:
        return len(self._items)

    #

    def get_items(self) -> ta.Sequence[TimelineItem]:
        return tuple(self._items)

    def get_item(self, item_id: TimelineItemId) -> TimelineItem | None:
        if (pos := self._positions_by_id.get(item_id)) is None:
            return None

        return self._items[pos - self._base_position]

    def get_position(self, item_id: TimelineItemId) -> int | None:
        return self._positions_by_id.get(item_id)

    def get_item_at_position(self, position: int) -> TimelineItem | None:
        idx = position - self._base_position
        if 0 <= idx < len(self._items):
            return self._items[idx]

        return None

    @property
    def first_position(self) -> int:
        return self._base_position

    @property
    def next_position(self) -> int:
        return self._base_position + len(self._items)

    #

    def _next_watermark(self) -> int:
        self._watermark += 1
        return self._watermark

    def append_item(self, item: TimelineItem) -> TimelineItemAppendedEvent:
        check.not_in(item.id, self._positions_by_id)

        position = self.next_position
        self._items.append(item)
        self._positions_by_id[item.id] = position

        return TimelineItemAppendedEvent(
            timeline_id=self._timeline_id,
            watermark=self._next_watermark(),
            item=item,
            position=position,
        )

    def _store_existing(self, item: TimelineItem) -> TimelineItem:
        pos = check.not_none(self._positions_by_id.get(item.id))

        old = self._items[pos - self._base_position]
        check.arg(item.revision > old.revision)

        self._items[pos - self._base_position] = item

        return old

    def update_item(self, item: TimelineItem) -> TimelineItemUpdatedEvent:
        """
        Replaces the stored item of the same id with `item` (whose revision must advance). The item's type may differ
        from the stored one - this is how transient streaming items are replaced by their canonical forms.
        """

        self._store_existing(item)

        return TimelineItemUpdatedEvent(
            timeline_id=self._timeline_id,
            watermark=self._next_watermark(),
            item=item,
        )

    def apply_item_delta(self, item: TimelineItem, appended: Content) -> TimelineItemDeltaEvent:
        """
        Stores `item` as `update_item` does, but describes the change as an incremental append to the item's streaming
        payload. The caller is responsible for `item` actually being `old` plus `appended`; the revision must advance
        by exactly 1.
        """

        old = self._store_existing(item)
        check.arg(item.revision == old.revision + 1)

        return TimelineItemDeltaEvent(
            timeline_id=self._timeline_id,
            watermark=self._next_watermark(),
            item_id=item.id,
            revision=item.revision,
            appended=appended,
        )
