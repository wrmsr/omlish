"""
The timeline event vocabulary. Every event carries its timeline's `watermark` - the per-timeline monotonic sequence
number assigned by the mutation that produced it. A snapshot taken at watermark W plus the events with watermark > W
reconstructs the live state exactly; this is the contract that makes attach/reconnect race-free (see the package
README).

There are deliberately only three kinds:
 - `TimelineItemAppendedEvent` - a new item, carrying it in full (including any initial streamed payload).
 - `TimelineItemUpdatedEvent` - an existing item changed non-incrementally, carrying its new full form. This covers
   state transitions, finalization, and live->canonical *replacement* (the item's type may differ from the one
   previously seen under the same id).
 - `TimelineItemDeltaEvent` - an existing item grew incrementally: `appended` extends the item-type's primary streaming
   text (an `AiStreamTimelineItem`'s content, a `ThinkingStreamTimelineItem`'s text, a STREAMING tool item's raw args).
   Carries the item's new `revision`, which always advances by exactly 1 per delta.

Finalization is item state (`item.finalized`), not an event kind.
"""
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...content.content import Content
from ...events.types import Event
from .items import TimelineId
from .items import TimelineItem
from .items import TimelineItemId


##


@dc.dataclass(frozen=True, kw_only=True)
class TimelineEvent(Event, lang.Abstract):
    timeline_id: TimelineId
    watermark: int


@dc.dataclass(frozen=True, kw_only=True)
class TimelineItemAppendedEvent(TimelineEvent, lang.Final):
    item: TimelineItem
    position: int


@dc.dataclass(frozen=True, kw_only=True)
class TimelineItemUpdatedEvent(TimelineEvent, lang.Final):
    item: TimelineItem


@dc.dataclass(frozen=True, kw_only=True)
class TimelineItemDeltaEvent(TimelineEvent, lang.Final):
    item_id: TimelineItemId
    revision: int
    appended: Content


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        TimelineItemAppendedEvent,
        TimelineItemUpdatedEvent,
        TimelineItemDeltaEvent,
    ]])
