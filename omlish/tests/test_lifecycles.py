import functools
import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import defs
from .. import lang


LifecycleT = ta.TypeVar('LifecycleT', bound='Lifecycle')
LifecycleCallback: ta.TypeAlias = ta.Callable[[LifecycleT], None]


class LifecycleStateError(Exception):
    pass


@dc.dataclass(frozen=True, eq=False)
@functools.total_ordering
class LifecycleState(lang.Final):
    name: str
    phase: int
    is_failed: bool

    def __lt__(self, other):
        return self.phase < check.isinstance(other, LifecycleState).phase


class LifecycleStates(lang.Namespace):
    NEW = LifecycleState('NEW', 0, False)

    CONSTRUCTING = LifecycleState('CONSTRUCTING', 1, False)
    FAILED_CONSTRUCTING = LifecycleState('FAILED_CONSTRUCTING', 2, True)
    CONSTRUCTED = LifecycleState('CONSTRUCTED', 3, False)

    STARTING = LifecycleState('STARTING', 5, False)
    FAILED_STARTING = LifecycleState('FAILED_STARTING', 6, True)
    STARTED = LifecycleState('STARTED', 7, False)

    STOPPING = LifecycleState('STOPPING', 8, False)
    FAILED_STOPPING = LifecycleState('FAILED_STOPPING', 9, True)
    STOPPED = LifecycleState('STOPPED', 10, False)

    DESTROYING = LifecycleState('DESTROYING', 11, False)
    FAILED_DESTROYING = LifecycleState('FAILED_DESTROYING', 12, True)
    DESTROYED = LifecycleState('DESTROYED', 13, False)


class Lifecycle:

    def lifecycle_construct(self) -> None:
        pass

    def lifecycle_start(self) -> None:
        pass

    def lifecycle_stop(self) -> None:
        pass

    def lifecycle_destroy(self) -> None:
        pass


@dc.dataclass(frozen=True, kw_only=True)
class CallbackLifecycle(Lifecycle, lang.Final, ta.Generic[LifecycleT]):
    on_construct: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None
    on_start: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None
    on_stop: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None
    on_destroy: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None

    def lifecycle_construct(self) -> None:
        if self.on_construct is not None:
            self.on_construct(self)

    def lifecycle_start(self) -> None:
        if self.on_start is not None:
            self.on_start(self)

    def lifecycle_stop(self) -> None:
        if self.on_stop is not None:
            self.on_stop(self)

    def lifecycle_destroy(self) -> None:
        if self.on_destroy is not None:
            self.on_destroy(self)


class LifecycleListener(ta.Generic[LifecycleT]):

    def on_starting(self, obj: LifecycleT) -> None:
        pass

    def on_started(self, obj: LifecycleT) -> None:
        pass

    def on_stopping(self, obj: LifecycleT) -> None:
        pass

    def on_stopped(self, obj: LifecycleT) -> None:
        pass


@dc.dataclass(frozen=True)
class LifecycleTransition(lang.Final):
    old: frozenset[LifecycleState]
    new_intermediate: LifecycleState
    new_failed: LifecycleState
    new_succeeded: LifecycleState

    def __post_init__(self) -> None:
        dc.maybe_post_init(super())
        check.unique([*self.old, self.new_intermediate, self.new_succeeded, self.new_failed])
        check.arg(all(self.new_intermediate > o for o in self.old))
        check.arg(self.new_failed > self.new_intermediate)
        check.arg(self.new_succeeded > self.new_failed)


class LifecycleTransitions(lang.Namespace):
    CONSTRUCT = LifecycleTransition(
        frozenset([LifecycleStates.NEW]),
        LifecycleStates.CONSTRUCTING,
        LifecycleStates.FAILED_CONSTRUCTING,
        LifecycleStates.CONSTRUCTED,
    )

    START = LifecycleTransition(
        frozenset([LifecycleStates.CONSTRUCTED]),
        LifecycleStates.STARTING,
        LifecycleStates.FAILED_STARTING,
        LifecycleStates.STARTED,
    )

    STOP = LifecycleTransition(
        frozenset([LifecycleStates.STARTED]),
        LifecycleStates.STOPPING,
        LifecycleStates.FAILED_STOPPING,
        LifecycleStates.STOPPED,
    )

    DESTROY = LifecycleTransition(
        frozenset([
            LifecycleStates.NEW,

            LifecycleStates.CONSTRUCTING,
            LifecycleStates.FAILED_CONSTRUCTING,
            LifecycleStates.CONSTRUCTED,

            LifecycleStates.STARTING,
            LifecycleStates.FAILED_STARTING,
            LifecycleStates.STARTED,

            LifecycleStates.STOPPING,
            LifecycleStates.FAILED_STOPPING,
            LifecycleStates.STOPPED,
        ]),
        LifecycleStates.DESTROYING,
        LifecycleStates.FAILED_DESTROYING,
        LifecycleStates.DESTROYED,
    )


class LifecycleController(Lifecycle, ta.Generic[LifecycleT]):

    def __init__(
            self,
            lifecycle: LifecycleT,
            *,
            lock: lang.DefaultLockable = None,
    ) -> None:
        super().__init__()

        self._lifecycle: LifecycleT = check.isinstance(lifecycle, Lifecycle)  # type: ignore
        self._lock = lang.default_lock(lock, True)

        self._state = LifecycleStates.NEW
        self._listeners: list[LifecycleListener[LifecycleT]] = []

    defs.repr('lifecycle', 'state')

    @property
    def lifecycle(self) -> LifecycleT:
        return self._lifecycle

    @property
    def state(self) -> LifecycleState:
        return self._state

    def add_listener(self, listener: LifecycleListener[LifecycleT]) -> 'LifecycleController':
        self._listeners.append(check.isinstance(listener, LifecycleListener))  # type: ignore
        return self

    def _advance(
            self,
            transition: LifecycleTransition,
            lifecycle_fn: ta.Callable[[], None],
            pre_listener_fn: ta.Callable[[LifecycleListener[LifecycleT]], ta.Callable[[LifecycleT], None]] | None = None,  # noqa
            post_listener_fn: ta.Callable[[LifecycleListener[LifecycleT]], ta.Callable[[LifecycleT], None]] | None = None,  # noqa
    ) -> None:
        with self._lock():
            if pre_listener_fn is not None:
                for listener in self._listeners:
                    pre_listener_fn(listener)(self._lifecycle)
            check.state(self._state in transition.old)
            self._state = transition.new_intermediate
            try:
                lifecycle_fn()
            except Exception:
                self._state = transition.new_failed
                raise
            self._state = transition.new_succeeded
            if post_listener_fn is not None:
                for listener in self._listeners:
                    post_listener_fn(listener)(self._lifecycle)

    def lifecycle_construct(self) -> None:
        self._advance(
            LifecycleTransitions.CONSTRUCT,
            self._lifecycle.lifecycle_construct,
        )

    def lifecycle_start(self) -> None:
        self._advance(
            LifecycleTransitions.START,
            self._lifecycle.lifecycle_start,
            lambda l: l.on_starting,
            lambda l: l.on_started,
        )

    def lifecycle_stop(self) -> None:
        self._advance(
            LifecycleTransitions.STOP,
            self._lifecycle.lifecycle_stop,
            lambda l: l.on_stopping,
            lambda l: l.on_stopped,
        )

    def lifecycle_destroy(self) -> None:
        self._advance(
            LifecycleTransitions.DESTROY,
            self._lifecycle.lifecycle_destroy,
        )


LifecycleManagerT = ta.TypeVar('LifecycleManagerT', bound='LifecycleManager')

class LifecycleManager:

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

        self._lock = lang.default_lock(lock, True)

        self._entries_by_lifecycle: ta.MutableMapping[Lifecycle, LifecycleManager.Entry] = col.IdentityKeyDict()

    @property
    def controller(self: LifecycleManagerT) -> 'LifecycleController[LifecycleManagerT]':
        return self.lifecycle_controller

    @property
    def state(self) -> LifecycleState:
        return self.lifecycle_controller.state

    @staticmethod
    def _get_controller(lifecycle: Lifecycle) -> LifecycleController:
        if isinstance(lifecycle, LifecycleController):
            return lifecycle
        elif isinstance(lifecycle, AbstractLifecycle):
            return lifecycle.lifecycle_controller
        elif isinstance(lifecycle, Lifecycle):
            return LifecycleController(lifecycle)
        else:
            raise TypeError(lifecycle)

    def _add_internal(self, lifecycle: Lifecycle, dependencies: ta.Iterable[Lifecycle]) -> Entry:
        check.state(self.state.phase < LifecycleStates.STOPPING.phase and not self.state.is_failed)

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
        check.state(self.state.phase < LifecycleStates.STOPPING.phase and not self.state.is_failed)

        with self._lock():
            entry = self._add_internal(lifecycle, dependencies)

            if self.state.phase >= LifecycleStates.CONSTRUCTING.phase:
                def rec(e):
                    if e.controller.state.phase < LifecycleStates.CONSTRUCTED.phase:
                        for dep in e.dependencies:
                            rec(dep)
                        e.controller.lifecycle_construct()
                rec(entry)
            if self.state.phase >= LifecycleStates.STARTING.phase:
                def rec(e):
                    if e.controller.state.phase < LifecycleStates.STARTED.phase:
                        for dep in e.dependencies:
                            rec(dep)
                        e.controller.lifecycle_start()
                rec(entry)

            return entry

    def construct(self) -> None:
        self.lifecycle_construct()

    def _do_lifecycle_construct(self) -> None:
        def rec(entry: LifecycleManager.Entry) -> None:
            for dep in entry.dependencies:
                rec(dep)
            if entry.controller.state.is_failed:
                raise LifecycleStateError(entry.controller)
            if entry.controller.state.phase < LifecycleStates.CONSTRUCTED.phase:
                entry.controller.lifecycle_construct()
        for entry in self._entries_by_lifecycle.values():
            rec(entry)

    def start(self) -> None:
        self.lifecycle_start()

    def _do_lifecycle_start(self) -> None:
        def rec(entry: LifecycleManager.Entry) -> None:
            for dep in entry.dependencies:
                rec(dep)
            if entry.controller.state.is_failed:
                raise LifecycleStateError(entry.controller)
            if entry.controller.state.phase < LifecycleStates.CONSTRUCTED.phase:
                entry.controller.lifecycle_construct()
            if entry.controller.state.phase < LifecycleStates.STARTED.phase:
                entry.controller.lifecycle_start()
        for entry in self._entries_by_lifecycle.values():
            rec(entry)

    def stop(self) -> None:
        self.lifecycle_stop()

    def _do_lifecycle_stop(self) -> None:
        def rec(entry: LifecycleManager.Entry) -> None:
            for dep in entry.dependents:
                rec(dep)
            if entry.controller.state.is_failed:
                raise LifecycleStateError(entry.controller)
            if entry.controller.state is LifecycleStates.STARTED:
                entry.controller.lifecycle_stop()
        for entry in self._entries_by_lifecycle.values():
            rec(entry)

    def destroy(self) -> None:
        self.lifecycle_destroy()

    def _do_lifecycle_destroy(self) -> None:
        def rec(entry: LifecycleManager.Entry) -> None:
            for dep in entry.dependents:
                rec(dep)
            if entry.controller.state.phase < LifecycleStates.DESTROYED.phase:
                entry.controller.lifecycle_destroy()
        for entry in self._entries_by_lifecycle.values():
            rec(entry)
