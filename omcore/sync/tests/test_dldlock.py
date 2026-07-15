# ruff: noqa: PT012 SLF001
"""
Tests for :mod:`dldlock`.

All concurrency tests use real ``threading.Thread`` instances.  Ordering is controlled with barriers, events, queues,
and blocking joins; no delay-based coordination is used.
"""
import gc
import os
import queue
import select
import signal
import threading
import traceback
import warnings
import weakref

import pytest

from ..dldlock import DeadlockDetectingLock
from ..dldlock import DeadlockDetectingLockError


TEST_TIMEOUT = 10.0


class ThreadGroup:
    """Start threads while preserving unexpected worker tracebacks."""

    def __init__(self):
        self._threads = []
        self._failures = queue.Queue()

    def start(self, target, name=None):
        def run():
            try:
                target()
            except BaseException:  # noqa
                self._failures.put(
                    (threading.current_thread().name, traceback.format_exc()),
                )

        thread = threading.Thread(target=run, name=name, daemon=True)
        thread.start()
        self._threads.append(thread)
        return thread

    def join(self):
        for thread in self._threads:
            thread.join(TEST_TIMEOUT)

        alive = [thread.name for thread in self._threads if thread.is_alive()]
        if alive:
            pytest.fail(f'threads did not finish: {alive!r}')

        failures = []
        while True:
            try:
                failures.append(self._failures.get_nowait())
            except queue.Empty:
                break

        if failures:
            formatted = '\n\n'.join(
                f'{name} failed:\n{tb}' for name, tb in failures
            )
            pytest.fail(formatted)


def wait_for(event, description):
    """Wait for an event, retaining a timeout only as a hang safeguard."""

    assert event.wait(TEST_TIMEOUT), f'timed out waiting for {description}'


def wait_at(barrier, description):
    """Enter a barrier, retaining a timeout only as a hang safeguard."""

    try:
        barrier.wait(TEST_TIMEOUT)
    except threading.BrokenBarrierError:
        pytest.fail(f'barrier broke while waiting for {description}')


def drain(q):
    """Return every item currently in a queue."""

    items = []
    while True:
        try:
            items.append(q.get_nowait())
        except queue.Empty:
            return items


def observe_contention(lock, expected_threads=1):
    """
    Return an event set after distinct threads take the contended path.

    ``DeadlockDetectingLock.acquire()`` calls ``has_deadlock()`` only after it has observed another owner.  Wrapping
    that method therefore gives tests a deterministic signal that a worker has reached the actual wait path.
    """

    original = lock.has_deadlock
    observed_thread_ids = set()
    observed_guard = threading.Lock()
    all_observed = threading.Event()

    def observed_has_deadlock():
        thread_id = threading.get_ident()
        with observed_guard:
            observed_thread_ids.add(thread_id)
            if len(observed_thread_ids) >= expected_threads:
                all_observed.set()
        return original()

    lock.has_deadlock = observed_has_deadlock
    return all_observed, observed_thread_ids


def exercise_cycle(size):
    """
    Run a staged ring-shaped wait cycle and return its outcomes.

    The first ``size - 1`` workers are admitted to their second acquisition one at a time.  Each is confirmed to be on
    the contended path before the next edge is added.  The final worker then closes the ring, making the deadlock
    deterministic rather than scheduler-dependent.
    """

    locks = [DeadlockDetectingLock() for _ in range(size)]
    first_locks_held = threading.Barrier(size + 1)
    may_attempt_second = [threading.Event() for _ in range(size)]
    waiting_edges = [threading.Event() for _ in range(size - 1)]
    outcomes = queue.Queue()
    thread_ids = queue.Queue()
    group = ThreadGroup()

    # Worker i waits on lock i + 1.  These wrappers prove that each non-closing
    # edge is present before the next worker is allowed to proceed.
    for index in range(size - 1):
        target_lock = locks[index + 1]
        original = target_lock.has_deadlock
        edge_observed = waiting_edges[index]

        def observed_has_deadlock(original=original, edge_observed=edge_observed):
            edge_observed.set()
            return original()

        target_lock.has_deadlock = observed_has_deadlock

    def make_worker(index):
        first = locks[index]
        second = locks[(index + 1) % size]

        def worker():
            acquired_second = False
            first.acquire()
            thread_ids.put(threading.get_ident())
            try:
                wait_at(first_locks_held, 'all cycle workers to own one lock')
                wait_for(
                    may_attempt_second[index],
                    f'cycle worker {index} to attempt its second lock',
                )
                try:
                    second.acquire()
                except DeadlockDetectingLockError as exc:
                    outcomes.put(('deadlock', index, str(exc)))
                else:
                    acquired_second = True
                    outcomes.put(('acquired', index, None))
            finally:
                if acquired_second:
                    second.release()
                first.release()

        return worker

    for index in range(size):
        group.start(make_worker(index), name=f'cycle-{index}')

    wait_at(first_locks_held, 'all first locks to be held')

    for index, edge_observed in enumerate(waiting_edges):
        may_attempt_second[index].set()
        wait_for(edge_observed, f'cycle wait edge {index}')

    # The last worker closes the already-established chain into a ring.
    may_attempt_second[-1].set()
    group.join()

    recorded = drain(outcomes)
    assert len(recorded) == size
    assert sum(kind == 'deadlock' for kind, _, _ in recorded) == 1
    assert all(kind in ('deadlock', 'acquired') for kind, _, _ in recorded)
    assert all(
        message is None or 'deadlock detected' in message
        for _, _, message in recorded
    )
    assert all(not lock.locked() for lock in locks)

    # A detected cycle must not poison future acquisitions.
    for lock in locks:
        assert lock.acquire() is True
        lock.release()

    # The per-thread wait-for entries are weak and scoped to acquire().
    gc.collect()
    for thread_id in drain(thread_ids):
        assert DeadlockDetectingLock._GlobalState.blocking_on.get(thread_id) is None

    return recorded


def run_in_forked_child(action):
    """Run ``action`` after fork and return its small status message."""

    read_fd, write_fd = os.pipe()
    with warnings.catch_warnings():
        warnings.filterwarnings(
            'ignore',
            message='This process .* is multi-threaded.*',
            category=DeprecationWarning,
        )
        pid = os.fork()

    if pid == 0:
        os.close(read_fd)
        try:
            action()
        except BaseException as exc:  # noqa
            payload = f'ERROR:{type(exc).__name__}:{exc}'.encode(
                'utf-8', 'replace',
            )
            exit_code = 1
        else:
            payload = b'OK'
            exit_code = 0

        try:
            os.write(write_fd, payload[:4096])
        finally:
            os.close(write_fd)
            os._exit(exit_code)

    os.close(write_fd)
    try:
        readable, _, _ = select.select([read_fd], [], [], TEST_TIMEOUT)
        if not readable:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
            pytest.fail('forked child did not report completion')

        payload = os.read(read_fd, 4096)
        _, status = os.waitpid(pid, 0)
    finally:
        os.close(read_fd)

    assert os.WIFEXITED(status), f'child status was {status!r}'
    assert os.WEXITSTATUS(status) == 0, payload.decode('utf-8', 'replace')
    return payload


def test_new_lock_starts_unlocked():
    lock = DeadlockDetectingLock()

    assert lock.locked() is False


def test_acquire_returns_true_and_release_unlocks():
    lock = DeadlockDetectingLock()

    assert lock.acquire() is True
    assert lock.locked() is True

    lock.release()
    assert lock.locked() is False


def test_lock_is_reentrant_and_tracks_recursion_depth():
    lock = DeadlockDetectingLock()

    assert lock.acquire() is True
    assert lock.acquire() is True
    assert lock.locked() is True

    lock.release()
    assert lock.locked() is True

    lock.release()
    assert lock.locked() is False


def test_context_manager_returns_lock_and_releases_after_exception():
    lock = DeadlockDetectingLock()

    class ExpectedError(Exception):
        pass

    with pytest.raises(ExpectedError):
        with lock as entered:
            assert entered is lock
            assert lock.locked() is True
            raise ExpectedError

    assert lock.locked() is False


def test_releasing_an_unlocked_lock_raises():
    lock = DeadlockDetectingLock()

    with pytest.raises(RuntimeError, match='cannot release un-acquired lock'):
        lock.release()


def test_only_the_owner_thread_can_release():
    lock = DeadlockDetectingLock()
    outcomes = queue.Queue()
    group = ThreadGroup()

    lock.acquire()

    def non_owner():
        try:
            lock.release()
        except RuntimeError as exc:
            outcomes.put(str(exc))
        else:
            raise AssertionError('a non-owner thread released the lock')

    try:
        group.start(non_owner, name='non-owner-release')
        group.join()

        assert drain(outcomes) == ['cannot release un-acquired lock']
        assert lock.locked() is True
    finally:
        lock.release()


def test_distinct_locks_do_not_serialize_each_other():
    locks = [DeadlockDetectingLock(), DeadlockDetectingLock()]
    both_inside = threading.Barrier(2)
    group = ThreadGroup()

    def make_worker(lock):
        def worker():
            with lock:
                wait_at(both_inside, 'workers holding independent locks')

        return worker

    group.start(make_worker(locks[0]), name='independent-0')
    group.start(make_worker(locks[1]), name='independent-1')
    group.join()

    assert all(not lock.locked() for lock in locks)


def test_contended_acquire_waits_and_is_woken_by_release():
    lock = DeadlockDetectingLock()
    contended, _ = observe_contention(lock)
    acquired = threading.Event()
    group = ThreadGroup()

    lock.acquire()

    def worker():
        lock.acquire()
        try:
            acquired.set()
        finally:
            lock.release()

    try:
        group.start(worker, name='contended-waiter')
        wait_for(contended, 'the waiter to reach the contended path')
        assert acquired.is_set() is False
    finally:
        lock.release()

    wait_for(acquired, 'the waiter to acquire after release')
    group.join()
    assert lock.locked() is False


def test_owner_can_reenter_while_another_thread_is_waiting():
    lock = DeadlockDetectingLock()
    contended, _ = observe_contention(lock)
    waiter_acquired = threading.Event()
    group = ThreadGroup()

    lock.acquire()

    def waiter():
        lock.acquire()
        try:
            waiter_acquired.set()
        finally:
            lock.release()

    group.start(waiter, name='reentrant-waiter')
    wait_for(contended, 'the waiter to block on the owner')

    assert lock.acquire() is True
    lock.release()

    # One recursion level is still held, so the waiter cannot have acquired.
    assert waiter_acquired.is_set() is False

    lock.release()
    wait_for(waiter_acquired, 'the waiter after the final recursive release')
    group.join()
    assert lock.locked() is False


def test_all_waiters_are_handed_the_lock_eventually():
    waiter_count = 8
    lock = DeadlockDetectingLock()
    all_contended, observed_thread_ids = observe_contention(
        lock, expected_threads=waiter_count,
    )
    begin = threading.Barrier(waiter_count + 1)
    acquisitions = queue.Queue()
    group = ThreadGroup()

    lock.acquire()

    def make_waiter(index):
        def waiter():
            wait_at(begin, 'all waiters to begin')
            lock.acquire()
            try:
                acquisitions.put(index)
            finally:
                lock.release()

        return waiter

    for index in range(waiter_count):
        group.start(make_waiter(index), name=f'waiter-{index}')

    wait_at(begin, 'main thread to release the waiter barrier')
    wait_for(all_contended, 'every waiter to reach the contended path')
    assert len(observed_thread_ids) == waiter_count
    assert acquisitions.empty()

    lock.release()
    group.join()

    assert sorted(drain(acquisitions)) == list(range(waiter_count))
    assert lock.locked() is False


def test_heavy_single_lock_contention_completes_without_false_deadlocks():
    thread_count = 8
    iterations = 250
    lock = DeadlockDetectingLock()
    begin = threading.Barrier(thread_count + 1)
    counter = [0]
    group = ThreadGroup()

    def worker():
        wait_at(begin, 'contention workers to begin')
        for _ in range(iterations):
            with lock:
                counter[0] += 1

    for index in range(thread_count):
        group.start(worker, name=f'stress-{index}')

    wait_at(begin, 'main thread to release the contention barrier')
    group.join()

    assert counter[0] == thread_count * iterations
    assert lock.locked() is False


@pytest.mark.parametrize('size', [2, 3], ids=['two-thread', 'three-thread'])
def test_wait_cycle_raises_deadlock_error_and_every_thread_finishes(size):
    recorded = exercise_cycle(size)

    assert sum(kind == 'deadlock' for kind, _, _ in recorded) >= 1


def test_acyclic_wait_chain_blocks_then_completes_without_deadlock_error():
    first = DeadlockDetectingLock()
    second = DeadlockDetectingLock()
    third = DeadlockDetectingLock()

    third_held = threading.Event()
    release_third = threading.Event()
    second_held = threading.Event()
    second_waiting_on_third, _ = observe_contention(third)
    first_waiting_on_second, _ = observe_contention(second)
    completed = queue.Queue()
    group = ThreadGroup()

    def tail_owner():
        third.acquire()
        try:
            third_held.set()
            wait_for(release_third, 'permission to release the tail lock')
        finally:
            third.release()
        completed.put('tail')

    def middle_waiter():
        wait_for(third_held, 'the tail thread to own the third lock')
        second.acquire()
        try:
            second_held.set()
            third.acquire()
            try:
                completed.put('middle')
            finally:
                third.release()
        finally:
            second.release()

    def head_waiter():
        wait_for(second_held, 'the middle thread to own the second lock')
        first.acquire()
        try:
            second.acquire()
            try:
                completed.put('head')
            finally:
                second.release()
        finally:
            first.release()

    group.start(tail_owner, name='chain-tail')
    group.start(middle_waiter, name='chain-middle')
    group.start(head_waiter, name='chain-head')

    wait_for(second_waiting_on_third, 'the middle wait edge')
    wait_for(first_waiting_on_second, 'the head wait edge')
    release_third.set()

    group.join()

    assert sorted(drain(completed)) == ['head', 'middle', 'tail']
    assert first.locked() is False
    assert second.locked() is False
    assert third.locked() is False


def test_global_registry_does_not_keep_ephemeral_locks_alive():
    lock = DeadlockDetectingLock()
    lock_id = id(lock)
    lock_ref = weakref.ref(lock)

    assert DeadlockDetectingLock._GlobalState.lock_registry.get(lock_id) is lock

    del lock
    gc.collect()

    assert lock_ref() is None
    assert DeadlockDetectingLock._GlobalState.lock_registry.get(lock_id) is None


@pytest.mark.skipif(
    not hasattr(os, 'fork') or not hasattr(os, 'register_at_fork'),
    reason='requires POSIX fork hooks',
)
def test_fork_preserves_recursion_owned_by_the_forking_thread():
    lock = DeadlockDetectingLock()
    lock.acquire()
    lock.acquire()

    def child_action():
        assert lock.locked() is True

        lock.release()
        assert lock.locked() is True

        lock.release()
        assert lock.locked() is False

        assert lock.acquire() is True
        lock.release()

    try:
        assert run_in_forked_child(child_action) == b'OK'

        # The parent retains its original ownership and recursion depth.
        assert lock.locked() is True
        lock.release()
        assert lock.locked() is True
        lock.release()
        assert lock.locked() is False
    finally:
        while lock.owner == threading.get_ident() and lock.locked():
            lock.release()


@pytest.mark.skipif(
    not hasattr(os, 'fork') or not hasattr(os, 'register_at_fork'),
    reason='requires POSIX fork hooks',
)
def test_fork_resets_a_lock_owned_by_a_vanished_thread():
    lock = DeadlockDetectingLock()
    owner_ready = threading.Event()
    release_owner = threading.Event()
    group = ThreadGroup()

    def owner():
        lock.acquire()
        try:
            owner_ready.set()
            wait_for(release_owner, 'the parent to release the owner thread')
        finally:
            lock.release()

    group.start(owner, name='pre-fork-owner')
    wait_for(owner_ready, 'the non-forking thread to own the lock')

    def child_action():
        assert lock.locked() is False
        assert lock.acquire() is True
        lock.release()

    try:
        assert run_in_forked_child(child_action) == b'OK'
        assert lock.locked() is True
    finally:
        release_owner.set()
        group.join()

    assert lock.locked() is False


@pytest.mark.skipif(
    not hasattr(os, 'fork') or not hasattr(os, 'register_at_fork'),
    reason='requires POSIX fork hooks',
)
def test_fork_discards_inherited_waiters_and_wait_graph_edges():
    lock = DeadlockDetectingLock()
    contended, _ = observe_contention(lock)
    owner_ready = threading.Event()
    release_owner = threading.Event()
    waiter_finished = threading.Event()
    waiter_ids = queue.Queue()
    group = ThreadGroup()

    def owner():
        lock.acquire()
        try:
            owner_ready.set()
            wait_for(release_owner, 'the parent to release the owner thread')
        finally:
            lock.release()

    def waiter():
        waiter_ids.put(threading.get_ident())
        lock.acquire()
        try:
            waiter_finished.set()
        finally:
            lock.release()

    group.start(owner, name='pre-fork-wait-graph-owner')
    wait_for(owner_ready, 'the non-forking thread to own the lock')
    group.start(waiter, name='pre-fork-wait-graph-waiter')
    wait_for(contended, 'the waiter to create a wait-for edge')

    blocked_thread_id = waiter_ids.get_nowait()
    assert DeadlockDetectingLock._GlobalState.blocking_on.get(blocked_thread_id)

    def child_action():
        # Neither the owner nor the waiter survives in the child.  Both the inherited lock state and the global wait-for
        # graph must be fresh.
        assert lock.locked() is False
        assert list(DeadlockDetectingLock._GlobalState.blocking_on.items()) == []
        with lock:
            assert lock.locked() is True

    try:
        assert run_in_forked_child(child_action) == b'OK'

        # Fork repair is child-only; the parent's owner and wait edge remain.
        assert lock.locked() is True
        assert DeadlockDetectingLock._GlobalState.blocking_on.get(blocked_thread_id)
    finally:
        release_owner.set()
        group.join()

    assert waiter_finished.is_set() is True
    assert lock.locked() is False
    gc.collect()
    assert DeadlockDetectingLock._GlobalState.blocking_on.get(blocked_thread_id) is None
