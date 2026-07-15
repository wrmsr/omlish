# ruff: noqa: PYI034 UP006 UP007 UP037 UP045
# @om-lite
"""
A re-entrant lock that detects deadlocks between threads.

The implementation is adapted from CPython's per-module import lock. It keeps only the machinery needed to represent a
thread/lock wait-for graph, detect a cycle before blocking, and wake waiting threads when an owner releases a lock.
"""
import threading
import typing as ta
import weakref

from ..os.forkhooks import ForkHook


##


class DeadlockDetectingLockError(RuntimeError):
    """Raised when acquiring a lock would create a deadlock."""


class DeadlockDetectingLock:
    """
    A recursive lock that raises :class:`DeadlockDetectingLockError` for wait cycles.

    The lock may be acquired repeatedly by its owning thread. If another thread would have to wait and the current
    wait-for graph already leads back to the current thread, ``acquire()`` raises ``DeadlockDetectingLockError`` instead
    of blocking forever.
    """

    def __init__(self) -> None:
        self._ForkHook.install()

        # This RLock protects this instance's owner/count/waiter state. An RLock is required because acquisition can be
        # re-entered by the same thread (for example from a signal handler or finalizer).
        self.lock = threading.RLock()
        self.wakeup = threading.Lock()

        self.owner: ta.Optional[int] = None

        # Lists are used, as in CPython's import lock, because append/pop are atomic in CPython and support the same
        # free-threaded implementation.
        self.count: ta.List[bool] = []
        self.waiters: ta.List[None] = []

        self._GlobalState.lock_registry[id(self)] = self

    class _LockList(list):
        """A list that can be held through a weak reference."""

        __slots__ = ('__weakref__',)

    class _GlobalState:
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

        # Map each thread to the locks that it is in the process of acquiring. The values are weak so this module does
        # not retain either stale per-thread state or the lock objects contained by that state.
        blocking_on: ta.ClassVar[ta.MutableMapping[int, 'DeadlockDetectingLock._LockList']] = weakref.WeakValueDictionary()  # noqa

        # Live lock instances are registered by identity solely so their inherited thread state can be repaired after
        # fork. Weak values ensure that the registry does not extend any instance's lifetime.
        lock_registry: ta.ClassVar[ta.MutableMapping[int, ta.Any]] = weakref.WeakValueDictionary()
        forking_thread_id: ta.ClassVar[ta.Optional[int]] = None

    class _ForkHook(ForkHook):
        @classmethod
        def _before_fork(cls) -> None:
            DeadlockDetectingLock._GlobalState.forking_thread_id = threading.get_ident()

        @classmethod
        def _after_fork_in_parent(cls) -> None:
            DeadlockDetectingLock._GlobalState.forking_thread_id = None

        @classmethod
        def _after_fork_in_child(cls) -> None:
            old_thread_id = DeadlockDetectingLock._GlobalState.forking_thread_id
            new_thread_id = threading.get_ident()

            # Other threads, and therefore their active wait-for edges, do not survive fork. Start the child with a
            # fresh graph.
            DeadlockDetectingLock._GlobalState.blocking_on = weakref.WeakValueDictionary()

            if old_thread_id is not None:
                for lock in list(DeadlockDetectingLock._GlobalState.lock_registry.values()):
                    lock._at_fork_reinit(old_thread_id, new_thread_id)  # noqa

            DeadlockDetectingLock._GlobalState.forking_thread_id = None

    def _at_fork_reinit(self, old_thread_id: int, new_thread_id: int) -> None:
        """Repair inherited state in the child process after ``fork()``."""

        recursion_depth = (
            len(self.count) if self.owner == old_thread_id else 0
        )

        # The internal synchronization primitives may have been held by a thread that does not exist in the child, so
        # replace them rather than attempting to acquire or release their inherited state.
        self.lock = threading.RLock()
        self.wakeup = threading.Lock()
        self.waiters = []

        if recursion_depth:
            self.owner = new_thread_id
            self.count = [True] * recursion_depth
        else:
            self.owner = None
            self.count = []

    @classmethod
    def _has_deadlocked(
            cls,
            target_id: int,
            *,
            seen_ids: ta.Set[ta.Optional[int]],
            candidate_ids: ta.Iterable[ta.Optional[int]],
            blocking_on: ta.Mapping[int, _LockList],
    ) -> bool:
        """Return whether ``target_id`` is reachable in a wait-for graph."""

        candidate_ids = list(candidate_ids)
        if target_id in candidate_ids:
            return True

        for thread_id in candidate_ids:
            if thread_id is None:
                continue

            candidate_blocking_on = blocking_on.get(thread_id)
            if not candidate_blocking_on:
                continue
            if thread_id in seen_ids:
                # The search reached a fixed point or a cycle that does not contain target_id, so it is not a deadlock
                # involving the current thread.
                return False
            seen_ids.add(thread_id)

            owners = [lock.owner for lock in candidate_blocking_on]
            if cls._has_deadlocked(
                    target_id,
                    seen_ids=seen_ids,
                    candidate_ids=owners,
                    blocking_on=blocking_on,
            ):
                return True

        return False

    def has_deadlock(self) -> bool:
        """Return whether waiting for this lock would deadlock this thread."""

        return self._has_deadlocked(
            target_id=threading.get_ident(),
            seen_ids=set(),
            candidate_ids=[self.owner],
            blocking_on=self._GlobalState.blocking_on,
        )

    class _BlockingOnManager:
        """Temporarily record that a thread is trying to acquire a lock."""

        def __init__(self, thread_id: int, lock: 'DeadlockDetectingLock') -> None:
            self.thread_id = thread_id
            self.lock = lock
            self.blocked_on: DeadlockDetectingLock._LockList

        def __enter__(self) -> None:
            self.blocked_on = DeadlockDetectingLock._GlobalState.blocking_on.setdefault(
                self.thread_id,
                DeadlockDetectingLock._LockList(),
            )
            self.blocked_on.append(self.lock)

        def __exit__(self, et, e, tb) -> None:
            self.blocked_on.remove(self.lock)

    def acquire(self) -> bool:
        """Acquire the lock, raising ``DeadlockDetectingLockError`` for a wait cycle."""

        thread_id = threading.get_ident()
        with self._BlockingOnManager(thread_id, self):
            while True:
                with self.lock:
                    if not self.count or self.owner == thread_id:
                        self.owner = thread_id
                        self.count.append(True)
                        return True

                    if self.has_deadlock():
                        raise DeadlockDetectingLockError(f'deadlock detected by {self!r}')

                    # The first waiter takes wakeup and records that release() must signal it. Other waiters join the
                    # same hand-off chain by blocking on wakeup below.
                    if self.wakeup.acquire(False):
                        self.waiters.append(None)

                # Wait until the owner releases the lock. Once awakened, pass wakeup on and retry the owner/count check
                # under self.lock.
                self.wakeup.acquire()
                self.wakeup.release()

    def release(self) -> None:
        """Release one recursion level of the lock."""

        thread_id = threading.get_ident()
        with self.lock:
            if self.owner != thread_id:
                raise RuntimeError('cannot release un-acquired lock')

            if not self.count:
                raise RuntimeError('lock acquire count mismatch')
            self.count.pop()
            if not self.count:
                self.owner = None
                if self.waiters:
                    self.waiters.pop()
                    self.wakeup.release()

    def locked(self) -> bool:
        """Return ``True`` when any thread owns the lock."""

        return bool(self.count)

    def __enter__(self) -> 'DeadlockDetectingLock':
        self.acquire()
        return self

    def __exit__(self, et, e, tb) -> None:
        self.release()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}() at {id(self):x}'
