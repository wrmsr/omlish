"""
The client-side half of a timeline: applies an initial window, subsequent events, and backward-paged windows to
maintain an ordered, id-keyed view - the exact state-machine every retained-UI frontend (textual, web DOM) needs, and
the reference consumer the coherence tests verify against.

Apply semantics:
 - `initialize(window)` - the attach window, once.
 - `apply_event(event)` - Appended inserts at the end; Updated replaces in place (the item's type may change - that's
   live->canonical replacement); Delta grows the item's streaming payload via `grow_streaming_item`.
 - `prepend_window(window)` - older items from `get_before` paging; *upserts*: items already present (window overlap
   from pairing extension or region seams) update in place rather than duplicating, per the windows-may-overlap
   contract.

Events for unknown item ids raise `TimelineProjectionError`: under the attach recipe they cannot occur, so one
occurring means a consumer bug (or, someday, eviction - revisit then).
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc

from ...content.content import Content
from .events import TimelineEvent
from .events import TimelineItemAppendedEvent
from .events import TimelineItemDeltaEvent
from .events import TimelineItemUpdatedEvent
from .history import TimelineWindow
from .items import AiStreamTimelineItem
from .items import ThinkingStreamTimelineItem
from .items import TimelineItem
from .items import TimelineItemId
from .items import ToolUseTimelineItem
from .items import ToolUseTimelineItemState


##


def grow_streaming_item(item: TimelineItem, appended: Content) -> TimelineItem:
    """
    Grows an in-flight item's primary streaming payload by `appended`, advancing its revision - the client-side
    realization of a `TimelineItemDeltaEvent`. Mirrors (and must remain equivalent to) what the manager's state holds
    after emitting one.
    """

    if isinstance(item, AiStreamTimelineItem):
        # FIXME:
        #  - lazy, collapse-on-access, linked-listy box thingy
        #  - also, like, resolve the fact deltas are only really defined for string concat'd markdown lol - non-lifted
        #    list content is intentionally undefined, configurably lifted to containers in
        #    LiftToStandardContentTransform
        new_content: Content
        if item.content is None:
            new_content = appended
        elif isinstance(item.content, str) and isinstance(appended, str):
            new_content = item.content + appended
        else:
            new_content = [item.content, appended]

        return dc.replace(
            item,
            revision=item.revision + 1,
            content=new_content,
        )

    elif isinstance(item, ThinkingStreamTimelineItem):
        return dc.replace(
            item,
            revision=item.revision + 1,
            text=item.text + check.isinstance(appended, str),
        )

    elif isinstance(item, ToolUseTimelineItem):
        check.state(item.state is ToolUseTimelineItemState.STREAMING)

        return dc.replace(
            item,
            revision=item.revision + 1,
            partial_raw_args=(item.partial_raw_args or '') + check.isinstance(appended, str),
        )

    else:
        raise TypeError(item)


##


class TimelineProjectionError(Exception):
    pass


@dc.dataclass()
class UnknownProjectionItemError(TimelineProjectionError):
    item_id: TimelineItemId


@dc.dataclass()
class StaleProjectionRevisionError(TimelineProjectionError):
    item_id: TimelineItemId
    have: int
    got: int


class TimelineProjection:
    def __init__(self) -> None:
        super().__init__()

        self._items: list[TimelineItem] = []
        self._indexes_by_id: dict[TimelineItemId, int] = {}

        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def items(self) -> ta.Sequence[TimelineItem]:
        return self._items

    def __len__(self) -> int:
        return len(self._items)

    def get_item(self, item_id: TimelineItemId) -> TimelineItem | None:
        if (idx := self._indexes_by_id.get(item_id)) is None:
            return None

        return self._items[idx]

    def get_index(self, item_id: TimelineItemId) -> int | None:
        return self._indexes_by_id.get(item_id)

    #

    def _set_items(self, items: ta.Sequence[TimelineItem]) -> None:
        self._items = list(items)
        self._indexes_by_id = {it.id: i for i, it in enumerate(self._items)}
        check.equal(len(self._indexes_by_id), len(self._items))

    def initialize(self, window: TimelineWindow) -> None:
        check.state(not self._initialized)
        self._initialized = True

        self._set_items(window.items)

    def prepend_window(self, window: TimelineWindow) -> ta.Sequence[TimelineItem]:
        """
        Applies an older (`get_before`) window: new items are prepended in order, already-known items (window
        overlap) are updated in place if newer. Returns the newly-inserted items, in order.
        """

        check.state(self._initialized)

        new_items: list[TimelineItem] = []

        for it in window.items:
            if (idx := self._indexes_by_id.get(it.id)) is not None:
                if it.revision > self._items[idx].revision:
                    self._items[idx] = it
            else:
                new_items.append(it)

        if new_items:
            self._set_items([*new_items, *self._items])

        return new_items

    #

    def apply_event(self, event: TimelineEvent) -> None:
        check.state(self._initialized)

        if isinstance(event, TimelineItemAppendedEvent):
            check.not_in(event.item.id, self._indexes_by_id)

            self._indexes_by_id[event.item.id] = len(self._items)
            self._items.append(event.item)

        elif isinstance(event, TimelineItemUpdatedEvent):
            if (idx := self._indexes_by_id.get(event.item.id)) is None:
                raise UnknownProjectionItemError(event.item.id)

            old = self._items[idx]
            if event.item.revision <= old.revision:
                raise StaleProjectionRevisionError(event.item.id, old.revision, event.item.revision)

            self._items[idx] = event.item

        elif isinstance(event, TimelineItemDeltaEvent):
            if (idx := self._indexes_by_id.get(event.item_id)) is None:
                raise UnknownProjectionItemError(event.item_id)

            old = self._items[idx]
            if event.revision != old.revision + 1:
                raise StaleProjectionRevisionError(event.item_id, old.revision, event.revision)

            new = grow_streaming_item(old, event.appended)
            check.equal(new.revision, event.revision)

            self._items[idx] = new

        else:
            raise TypeError(event)
