# ruff: noqa: UP006 UP007
import typing as ta

from .configs import ProcessGroupConfig
from .dispatchers import Dispatchers
from .events import EventCallbacks
from .events import ProcessGroupAddedEvent
from .events import ProcessGroupRemovedEvent
from .types import HasDispatchers
from .types import Process
from .types import ProcessGroup
from .utils.collections import KeyedCollectionAccessors


class ProcessGroupManager(
    KeyedCollectionAccessors[str, ProcessGroup],
    HasDispatchers,
):
    def __init__(
            self,
            *,
            event_callbacks: EventCallbacks,
    ) -> None:
        super().__init__()

        self._event_callbacks = event_callbacks

        self._by_name: ta.Dict[str, ProcessGroup] = {}

    @property
    def _by_key(self) -> ta.Mapping[str, ProcessGroup]:
        return self._by_name

    #

    def all_processes(self) -> ta.Iterator[Process]:
        for g in self:
            yield from g

    #

    def get_dispatchers(self) -> Dispatchers:
        return Dispatchers(
            d
            for g in self
            for p in g
            for d in p.get_dispatchers()
        )

    #

    def add(self, group: ProcessGroup) -> None:
        if (name := group.name) in self._by_name:
            raise KeyError(f'Process group already exists: {name}')

        self._by_name[name] = group

        self._event_callbacks.notify(ProcessGroupAddedEvent(name))

    def remove(self, name: str) -> None:
        group = self._by_name[name]

        group.before_remove()

        del self._by_name[name]

        self._event_callbacks.notify(ProcessGroupRemovedEvent(name))

    def clear(self) -> None:
        # FIXME: events?
        self._by_name.clear()

    #

    class Diff(ta.NamedTuple):
        added: ta.List[ProcessGroupConfig]
        changed: ta.List[ProcessGroupConfig]
        removed: ta.List[ProcessGroupConfig]

    def diff(self, new: ta.Sequence[ProcessGroupConfig]) -> Diff:
        cur = [group.config for group in self]

        cur_by_name = {cfg.name: cfg for cfg in cur}
        new_by_name = {cfg.name: cfg for cfg in new}

        added = [cand for cand in new if cand.name not in cur_by_name]
        removed = [cand for cand in cur if cand.name not in new_by_name]
        changed = [cand for cand in new if cand != cur_by_name.get(cand.name, cand)]

        return ProcessGroupManager.Diff(
            added,
            changed,
            removed,
        )
