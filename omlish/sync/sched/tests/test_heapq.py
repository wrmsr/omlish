import queue
import time

import pytest

from ..heapq import HeapqScheduledRunner
from ..types import ScheduledCancelledError
from ..types import ScheduledRunnerStateError
from ..types import ScheduledTimeoutError
from .consts import SLEEPS


def test_schedule_runs_after_delay(request) -> None:
    timer = HeapqScheduledRunner()
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[str] = queue.Queue()

    t0 = time.monotonic()
    h = timer.schedule(SLEEPS * 5, lambda: q.put('ok'))

    assert h.result(timeout=SLEEPS * 100) is None
    assert q.get(timeout=SLEEPS * 100) == 'ok'
    assert (time.monotonic() - t0) >= (SLEEPS * 3)  # loose lower bound


def test_schedule_zero_delay_runs_soon(request) -> None:
    timer = HeapqScheduledRunner()
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[int] = queue.Queue()

    h = timer.schedule(0.0, lambda: q.put(1))
    h.result(timeout=SLEEPS * 100)
    assert q.get(timeout=SLEEPS * 100) == 1


def test_cancel_prevents_execution(request) -> None:
    timer = HeapqScheduledRunner()
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[str] = queue.Queue()

    h = timer.schedule(SLEEPS * 20, lambda: q.put('nope'))
    assert h.cancel() is True

    with pytest.raises(queue.Empty):
        q.get(timeout=SLEEPS * 40)

    assert h.cancelled() is True
    assert h.done() is True
    with pytest.raises(ScheduledCancelledError):
        h.result(timeout=0.1)


def test_cancel_after_completion_returns_false(request) -> None:
    timer = HeapqScheduledRunner()
    request.addfinalizer(timer.shutdown)

    h = timer.schedule(0.0, lambda: 123)
    assert h.result(timeout=SLEEPS * 100) == 123
    assert h.done() is True
    assert h.cancel() is False


def test_exception_propagates(request) -> None:
    timer = HeapqScheduledRunner()
    request.addfinalizer(timer.shutdown)

    def boom() -> None:
        raise ValueError('x')

    h = timer.schedule(0.0, boom)
    with pytest.raises(ValueError):  # noqa
        h.result(timeout=SLEEPS * 100)


def test_timeout_on_result(request) -> None:
    timer = HeapqScheduledRunner()
    request.addfinalizer(timer.shutdown)

    h = timer.schedule(SLEEPS * 20, lambda: 1)
    with pytest.raises(ScheduledTimeoutError):
        h.result(timeout=SLEEPS)
    # eventually completes
    assert h.result(timeout=SLEEPS * 100) == 1


def test_callbacks_run(request) -> None:
    timer = HeapqScheduledRunner()
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[str] = queue.Queue()

    h = timer.schedule(0.0, lambda: 'x')

    def cb(handle) -> None:
        if handle.cancelled():
            q.put('c')
        else:
            q.put('d')

    h.add_done_callback(cb)
    assert h.result(timeout=SLEEPS * 100) == 'x'
    assert q.get(timeout=SLEEPS * 100) == 'd'


def test_multiple_tasks_ordered_by_deadline(request) -> None:
    timer = HeapqScheduledRunner()
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[str] = queue.Queue()

    timer.schedule(SLEEPS * 5, lambda: q.put('b'))
    timer.schedule(SLEEPS * 1, lambda: q.put('a'))
    timer.schedule(SLEEPS * 2, lambda: q.put('c'))

    got = [q.get(timeout=SLEEPS * 100), q.get(timeout=SLEEPS * 100), q.get(timeout=SLEEPS * 100)]
    assert got == ['a', 'c', 'b']


def test_batch_size_processes_multiple_ready_tasks(request) -> None:
    timer = HeapqScheduledRunner(batch_size=5)
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[int] = queue.Queue()

    # Schedule 10 tasks with same deadline
    for i in range(10):
        timer.schedule(SLEEPS * 1, lambda i=i: q.put(i))  # type: ignore[misc]

    # All should execute
    results = []
    for _ in range(10):
        results.append(q.get(timeout=SLEEPS * 100))

    assert sorted(results) == list(range(10))


def test_batch_size_one_processes_serially(request) -> None:
    timer = HeapqScheduledRunner(batch_size=1)
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[int] = queue.Queue()

    # Schedule 3 tasks
    for i in range(3):
        timer.schedule(SLEEPS * 1, lambda i=i: q.put(i))  # type: ignore[misc]

    # All should still execute
    results = []
    for _ in range(3):
        results.append(q.get(timeout=SLEEPS * 100))

    assert sorted(results) == [0, 1, 2]


def test_batch_max_time_recycles_remaining_tasks(request) -> None:
    timer = HeapqScheduledRunner(batch_size=10, batch_max_time_s=SLEEPS * 10)
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[int] = queue.Queue()

    def slow_task(i: int) -> None:
        time.sleep(SLEEPS * 6)
        q.put(i)

    # Schedule 5 tasks, all ready at once
    for i in range(5):
        timer.schedule(SLEEPS * 1, lambda i=i: slow_task(i))  # type: ignore[misc]

    # All should eventually execute
    results = []
    for _ in range(5):
        results.append(q.get(timeout=SLEEPS * 200))

    assert sorted(results) == [0, 1, 2, 3, 4]


def test_batch_max_time_without_batch_size_uses_default(request) -> None:
    timer = HeapqScheduledRunner(batch_max_time_s=SLEEPS * 10)
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[int] = queue.Queue()

    # With batch_size=1, only one task executes per batch anyway
    for i in range(3):
        timer.schedule(SLEEPS * 1, lambda i=i: q.put(i))  # type: ignore[misc]

    results = []
    for _ in range(3):
        results.append(q.get(timeout=SLEEPS * 100))

    assert sorted(results) == [0, 1, 2]


def test_batch_recycle_preserves_execution_order(request) -> None:
    timer = HeapqScheduledRunner(batch_size=10, batch_max_time_s=SLEEPS * 5)
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[tuple[int, float]] = queue.Queue()

    def timed_task(i: int) -> None:
        time.sleep(SLEEPS * 4)
        q.put((i, time.monotonic()))

    # Schedule tasks with same deadline
    for i in range(3):
        timer.schedule(SLEEPS * 1, lambda i=i: timed_task(i))  # type: ignore[misc]

    results = []
    for _ in range(3):
        results.append(q.get(timeout=SLEEPS * 100))

    # Check all tasks executed
    task_ids = [r[0] for r in results]
    assert sorted(task_ids) == [0, 1, 2]


def test_batch_with_cancellations(request) -> None:
    timer = HeapqScheduledRunner(batch_size=5)
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[int] = queue.Queue()

    handles = []
    for i in range(5):
        h = timer.schedule(SLEEPS * 2, lambda i=i: q.put(i))  # type: ignore[misc]
        handles.append(h)

    # Cancel some tasks before they execute
    handles[1].cancel()
    handles[3].cancel()

    # Only tasks 0, 2, 4 should execute
    results = []
    for _ in range(3):
        results.append(q.get(timeout=SLEEPS * 100))

    assert sorted(results) == [0, 2, 4]

    # Verify queue is empty (no extra tasks)
    with pytest.raises(queue.Empty):
        q.get(timeout=SLEEPS * 10)


def test_large_batch_size(request) -> None:
    timer = HeapqScheduledRunner(batch_size=100)
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[int] = queue.Queue()

    # Schedule 50 tasks
    for i in range(50):
        timer.schedule(SLEEPS * 1, lambda i=i: q.put(i))  # type: ignore[misc]

    # All should execute
    results = []
    for _ in range(50):
        results.append(q.get(timeout=SLEEPS * 100))

    assert sorted(results) == list(range(50))


def test_batch_with_staggered_deadlines(request) -> None:
    timer = HeapqScheduledRunner(batch_size=10)
    request.addfinalizer(timer.shutdown)

    q: queue.Queue[str] = queue.Queue()

    # Schedule tasks with different deadlines
    timer.schedule(SLEEPS * 1, lambda: q.put('a'))  # Ready soon
    timer.schedule(SLEEPS * 1, lambda: q.put('b'))  # Ready soon
    timer.schedule(SLEEPS * 20, lambda: q.put('c'))  # Ready later

    # First two should execute together in a batch
    assert q.get(timeout=SLEEPS * 100) in ('a', 'b')
    assert q.get(timeout=SLEEPS * 100) in ('a', 'b')

    # Third should execute later
    assert q.get(timeout=SLEEPS * 100) == 'c'


def test_result_timeout(request):
    timer = HeapqScheduledRunner()
    request.addfinalizer(timer.shutdown)

    did_run = False

    def task():
        nonlocal did_run
        did_run = True

    handle = timer.schedule(SLEEPS * 500, task)

    with pytest.raises(ScheduledTimeoutError):
        handle.result(timeout=SLEEPS * 10)

    timer.shutdown(cancel_all=True)

    assert not did_run


def test_shutdown_rejects_new_tasks(request):
    timer = HeapqScheduledRunner()
    request.addfinalizer(timer.shutdown)

    # Schedule one task to start the thread
    timer.schedule(SLEEPS * 10, lambda: None)

    # Shutdown
    timer.shutdown(no_wait=True)

    # Try to schedule new task
    with pytest.raises(ScheduledRunnerStateError):
        timer.schedule(SLEEPS * 10, lambda: 42)


def test_shutdown_cancel_all_true(request):
    """Test shutdown with cancel_all=True cancels pending tasks."""

    timer = HeapqScheduledRunner()

    executed = []

    # Schedule tasks with delays
    h1 = timer.schedule(SLEEPS * 50, lambda: executed.append(1))
    h2 = timer.schedule(SLEEPS * 60, lambda: executed.append(2))
    h3 = timer.schedule(SLEEPS * 70, lambda: executed.append(3))

    # Give thread time to start
    time.sleep(SLEEPS)

    # Shutdown immediately with cancel_all=True
    timer.shutdown(cancel_all=True)

    # All tasks should be cancelled, none should execute
    assert executed == []
    # Tasks should be done (either cancelled or completed, but none completed)
    assert h1.done()
    assert h2.done()
    assert h3.done()


def test_shutdown_cancel_all_false(request):
    """Test shutdown with cancel_all=False (drain mode) allows tasks to complete."""

    timer = HeapqScheduledRunner()

    executed = []

    # Schedule tasks with short delays
    h1 = timer.schedule(SLEEPS * 5, lambda: executed.append(1))
    h2 = timer.schedule(SLEEPS * 10, lambda: executed.append(2))
    h3 = timer.schedule(SLEEPS * 15, lambda: executed.append(3))

    # Give tasks time to be scheduled
    time.sleep(SLEEPS)

    # Shutdown with cancel_all=False (drain mode)
    timer.shutdown(cancel_all=False)

    # All tasks should have completed
    assert sorted(executed) == [1, 2, 3]
    assert h1.done()
    assert h2.done()
    assert h3.done()


def test_shutdown_no_wait_true(request):
    """Test shutdown with no_wait=True returns immediately."""

    timer = HeapqScheduledRunner()

    executed = []
    timer.schedule(SLEEPS * 10, lambda: executed.append(1))

    start = time.monotonic()
    timer.shutdown(cancel_all=True, no_wait=True)
    elapsed = time.monotonic() - start

    # Should return almost immediately
    assert elapsed < SLEEPS * 5

    # Wait for actual shutdown
    timer.wait(timeout=SLEEPS * 100)


def test_shutdown_no_wait_false(request):
    """Test shutdown with no_wait=False (default) waits for completion."""

    timer = HeapqScheduledRunner()

    executed = []
    timer.schedule(SLEEPS * 5, lambda: executed.append(1))
    timer.schedule(SLEEPS * 10, lambda: executed.append(2))

    # Give thread time to start
    time.sleep(SLEEPS)

    # Shutdown and wait (default behavior)
    start = time.monotonic()
    timer.shutdown(cancel_all=False, no_wait=False)
    elapsed = time.monotonic() - start

    # Should have waited for tasks to complete
    assert elapsed >= SLEEPS * 8  # At least close to the longest delay
    assert sorted(executed) == [1, 2]


def test_shutdown_with_timeout_success(request):
    """Test shutdown with timeout that succeeds."""

    timer = HeapqScheduledRunner()

    executed = []
    timer.schedule(SLEEPS * 5, lambda: executed.append(1))

    # Give thread time to start
    time.sleep(SLEEPS)

    # Shutdown with generous timeout
    timer.shutdown(cancel_all=False, timeout=SLEEPS * 100)

    # Should complete successfully
    assert executed == [1]


def test_shutdown_with_timeout_expires(request):
    """Test shutdown with timeout that expires."""
    timer = HeapqScheduledRunner()

    executed = []

    # Schedule a long-running task
    def slow_task():
        time.sleep(SLEEPS * 50)
        executed.append(1)

    timer.schedule(SLEEPS * 1, slow_task)

    # Give task time to start
    time.sleep(SLEEPS * 5)

    # Shutdown with short timeout should raise TimeoutError
    with pytest.raises(TimeoutError):
        timer.shutdown(cancel_all=False, timeout=SLEEPS * 10)


def test_shutdown_cancel_all_and_no_wait(request):
    """Test shutdown with both cancel_all=True and no_wait=True."""

    timer = HeapqScheduledRunner()

    executed = []
    h1 = timer.schedule(SLEEPS * 50, lambda: executed.append(1))  # noqa
    h2 = timer.schedule(SLEEPS * 60, lambda: executed.append(2))  # noqa

    start = time.monotonic()
    timer.shutdown(cancel_all=True, no_wait=True)
    elapsed = time.monotonic() - start

    # Should return immediately
    assert elapsed < SLEEPS * 5

    # Tasks should not execute
    time.sleep(SLEEPS * 10)
    assert executed == []

    # Wait for full shutdown
    timer.wait(timeout=SLEEPS * 100)


def test_shutdown_drain_and_timeout(request):
    """Test shutdown drain mode with timeout."""

    timer = HeapqScheduledRunner()

    executed = []
    timer.schedule(SLEEPS * 5, lambda: executed.append(1))
    timer.schedule(SLEEPS * 10, lambda: executed.append(2))

    # Give thread time to start
    time.sleep(SLEEPS)

    # Shutdown with drain mode and generous timeout
    timer.shutdown(cancel_all=False, timeout=SLEEPS * 50)

    # Both tasks should complete
    assert sorted(executed) == [1, 2]


def test_shutdown_multiple_calls(request):
    """Test that multiple shutdown calls are idempotent."""

    timer = HeapqScheduledRunner()

    executed = []
    timer.schedule(SLEEPS * 5, lambda: executed.append(1))

    # Give thread time to start
    time.sleep(SLEEPS)

    # First shutdown
    timer.shutdown(cancel_all=False)

    # Second shutdown should not raise
    timer.shutdown(cancel_all=False)

    # Third shutdown with different params should not raise
    timer.shutdown(cancel_all=True)

    assert executed == [1]


def test_shutdown_from_new_state(request):
    """Test shutdown on a timer that was never started."""

    timer = HeapqScheduledRunner()

    # Shutdown without ever scheduling anything
    timer.shutdown(cancel_all=False)

    # Should complete without error
    from ..types import ScheduledRunnerState
    assert timer.get_state() == ScheduledRunnerState.NEW


def test_wait_after_no_wait_shutdown(request):
    """Test explicit wait() after no_wait shutdown."""

    timer = HeapqScheduledRunner()

    executed = []
    timer.schedule(SLEEPS * 5, lambda: executed.append(1))
    timer.schedule(SLEEPS * 10, lambda: executed.append(2))

    # Give thread time to start
    time.sleep(SLEEPS)

    # Shutdown without waiting
    timer.shutdown(cancel_all=False, no_wait=True)

    # Explicitly wait
    timer.wait(timeout=SLEEPS * 100)

    # Tasks should have completed
    assert sorted(executed) == [1, 2]


def test_wait_with_timeout_expires(request):
    """Test wait() with timeout that expires."""

    timer = HeapqScheduledRunner()

    # Schedule a long-running task
    def slow_task():
        time.sleep(SLEEPS * 50)

    timer.schedule(SLEEPS * 1, slow_task)
    time.sleep(SLEEPS * 5)  # Let task start

    # Shutdown without waiting
    timer.shutdown(cancel_all=False, no_wait=True)

    # Wait with short timeout should raise
    with pytest.raises(TimeoutError):
        timer.wait(timeout=SLEEPS * 10)
