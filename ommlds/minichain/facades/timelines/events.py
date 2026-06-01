import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...events.types import Event
from .items import TimelineId
from .items import TimelineItem


##


@dc.dataclass(frozen=True, kw_only=True)
class TimelineEvent(Event, lang.Abstract):
    timeline_id: TimelineId


@dc.dataclass(frozen=True, kw_only=True)
class TimelineItemAppendedEvent(TimelineEvent, lang.Final):
    item: TimelineItem


@dc.dataclass(frozen=True, kw_only=True)
class TimelineItemUpdatedEvent(TimelineEvent, lang.Final):
    item: TimelineItem


@dc.dataclass(frozen=True, kw_only=True)
class TimelineItemFinalizedEvent(TimelineEvent, lang.Final):
    item: TimelineItem


@dc.dataclass(frozen=True, kw_only=True)
class TimelineItemsPrependedEvent(TimelineEvent, lang.Final):
    items: ta.Sequence[TimelineItem]


@dc.dataclass(frozen=True, kw_only=True)
class TimelineResetEvent(TimelineEvent, lang.Final):
    pass


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        TimelineItemAppendedEvent,
        TimelineItemUpdatedEvent,
        TimelineItemFinalizedEvent,
        TimelineItemsPrependedEvent,
        TimelineResetEvent,
    ]])
