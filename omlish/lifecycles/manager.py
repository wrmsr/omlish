import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import lang
from .abstract import AbstractLifecycle
from .base import Lifecycle
from .controller import LifecycleController
from .states import LifecycleState
from .states import LifecycleStateError
from .states import LifecycleStates


class LifecycleManager(AbstractLifecycle):

    @dc.dataclass(frozen=True)
    class Entry(lang.Final):
        controller: LifecycleController
        dependencies: ta.MutableSet['LifecycleManager.Entry'] = dc.field(default_factory=col.IdentitySet)
        dependents: ta.MutableSet['LifecycleManager.Entry'] = dc.field(default_factory=col.IdentitySet)

    def __init__(
            self,
            *,
            lock: lang.DefaultLockable = None,
    ) -> None:
        super().__init__()

        self._lock = lang.default_lock(lock, False)

        self._entries_by_lifecycle: ta.MutableMapping[Lifecycle, LifecycleManager.Entry] = col.IdentityKeyDict()

        self._controller = LifecycleController(self._lifecycle, lock=self._lock)

    @property
    def controller(self) -> LifecycleController:
        return self._controller

    @property
    def state(self) -> LifecycleState:
        return self._controller.state

    @staticmethod
    def _get_controller(lifecycle: Lifecycle) -> LifecycleController:
        if isinstance(lifecycle, LifecycleController):
            return lifecycle
        # elif isinstance(lifecycle, AbstractLifecycle):
        #     return lifecycle.lifecycle_controller
        elif isinstance(lifecycle, Lifecycle):
            return LifecycleController(lifecycle)
        else:
            raise TypeError(lifecycle)

    def _add_internal(self, lifecycle: Lifecycle, dependencies: ta.Iterable[Lifecycle]) -> Entry:
        check.state(self.state < LifecycleStates.STOPPING and not self.state.is_failed)

        check.isinstance(lifecycle, Lifecycle)
        try:
            entry = self._entries_by_lifecycle[lifecycle]
        except KeyError:
            controller = self._get_controller(lifecycle)
            entry = self._entries_by_lifecycle[lifecycle] = LifecycleManager.Entry(controller)

        for dep in dependencies:
            check.isinstance(dep, Lifecycle)
            dep_entry = self._add_internal(dep, [])
            entry.dependencies.add(dep_entry)
            dep_entry.dependents.add(entry)

        return entry

    def add(
            self,
            lifecycle: Lifecycle,
            dependencies: ta.Iterable[Lifecycle] = (),
    ) -> Entry:
        check.state(self.state < LifecycleStates.STOPPING and not self.state.is_failed)

        with self._lock():
            entry = self._add_internal(lifecycle, dependencies)

            if self.state >= LifecycleStates.CONSTRUCTING:
                def rec(e):
                    if e.controller.state < LifecycleStates.CONSTRUCTED:
                        for dep in e.dependencies:
                            rec(dep)
                        e.controller.lifecycle_construct()
                rec(entry)

            if self.state >= LifecycleStates.STARTING:
                def rec(e):
                    if e.controller.state < LifecycleStates.STARTED:
                        for dep in e.dependencies:
                            rec(dep)
                        e.controller.lifecycle_start()
                rec(entry)

            return entry

    ##

    @ta.override
    def _lifecycle_construct(self) -> None:
        def rec(entry: LifecycleManager.Entry) -> None:
            for dep in entry.dependencies:
                rec(dep)

            if entry.controller.state.is_failed:
                raise LifecycleStateError(entry.controller)

            if entry.controller.state < LifecycleStates.CONSTRUCTED:
                entry.controller.lifecycle_construct()

        for entry in self._entries_by_lifecycle.values():
            rec(entry)

    @ta.override
    def _lifecycle_start(self) -> None:
        def rec(entry: LifecycleManager.Entry) -> None:
            for dep in entry.dependencies:
                rec(dep)

            if entry.controller.state.is_failed:
                raise LifecycleStateError(entry.controller)

            if entry.controller.state < LifecycleStates.CONSTRUCTED:
                entry.controller.lifecycle_construct()

            if entry.controller.state < LifecycleStates.STARTED:
                entry.controller.lifecycle_start()

        for entry in self._entries_by_lifecycle.values():
            rec(entry)

    @ta.override
    def _lifecycle_stop(self) -> None:
        def rec(entry: LifecycleManager.Entry) -> None:
            for dep in entry.dependents:
                rec(dep)

            if entry.controller.state.is_failed:
                raise LifecycleStateError(entry.controller)

            if entry.controller.state is LifecycleStates.STARTED:
                entry.controller.lifecycle_stop()

        for entry in self._entries_by_lifecycle.values():
            rec(entry)

    @ta.override
    def _lifecycle_destroy(self) -> None:
        def rec(entry: LifecycleManager.Entry) -> None:
            for dep in entry.dependents:
                rec(dep)

            if entry.controller.state < LifecycleStates.DESTROYED:
                entry.controller.lifecycle_destroy()

        for entry in self._entries_by_lifecycle.values():
            rec(entry)
