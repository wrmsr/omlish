# ruff: noqa: UP006 UP007
import typing as ta

from .collections import KeyedCollectionAccessors
from .events import EventCallbacks
from .events import ProcessGroupAddedEvent
from .events import ProcessGroupRemovedEvent
from .types import Process
from .types import ProcessGroup


class ProcessGroupManager(KeyedCollectionAccessors[str, ProcessGroup]):
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
