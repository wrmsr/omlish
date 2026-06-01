import typing as ta

from omlish import check
from omlish import dataclasses as dc

from .events import TimelineEvent
from .events import TimelineItemAppendedEvent
from .events import TimelineItemFinalizedEvent
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
            items: ta.Iterable[TimelineItem] = (),
    ) -> None:
        super().__init__()

        self._timeline_id = timeline_id

        self._items: list[TimelineItem] = []
        self._items_by_id: dict[TimelineItemId, TimelineItem] = {}

        for item in items:
            self._append_existing_item(item)

    @property
    def timeline_id(self) -> TimelineId:
        return self._timeline_id

    def get_items(self) -> ta.Sequence[TimelineItem]:
        return tuple(self._items)

    def get_item(self, item_id: TimelineItemId) -> TimelineItem | None:
        return self._items_by_id.get(item_id)

    def get_item_ordinal(self, item_id: TimelineItemId) -> int | None:
        for i, item in enumerate(self._items):
            if item.id == item_id:
                return i

        return None

    def get_item_by_ordinal(self, ordinal: int) -> TimelineItem | None:
        if 0 <= ordinal < len(self._items):
            return self._items[ordinal]

        return None

    def __len__(self) -> int:
        return len(self._items)

    #

    def _append_existing_item(self, item: TimelineItem) -> None:
        check.not_in(item.id, self._items_by_id)

        self._items.append(item)
        self._items_by_id[item.id] = item

    def append_item(self, item: TimelineItem) -> TimelineEvent:
        self._append_existing_item(item)

        return TimelineItemAppendedEvent(
            timeline_id=self._timeline_id,
            item=item,
        )

    def update_item(self, item: TimelineItem) -> TimelineEvent:
        old = check.not_none(self._items_by_id.get(item.id))
        check.arg(item.revision > old.revision)

        ordinal = check.not_none(self.get_item_ordinal(item.id))
        self._items[ordinal] = item
        self._items_by_id[item.id] = item

        return TimelineItemUpdatedEvent(
            timeline_id=self._timeline_id,
            item=item,
        )

    def replace_item(self, item: TimelineItem) -> TimelineEvent:
        if item.id in self._items_by_id:
            return self.update_item(item)

        return self.append_item(item)

    def finalize_item(self, item_id: TimelineItemId) -> TimelineEvent:
        old = check.not_none(self._items_by_id.get(item_id))
        if old.finalized:
            item = old
        else:
            item = dc.replace(
                old,
                revision=old.revision + 1,
                finalized=True,
            )

            ordinal = check.not_none(self.get_item_ordinal(item_id))
            self._items[ordinal] = item
            self._items_by_id[item.id] = item

        return TimelineItemFinalizedEvent(
            timeline_id=self._timeline_id,
            item=item,
        )
