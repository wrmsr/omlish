import queue
import threading
import time

import pytest

from ..heapq import HeapqScheduledRunner
from ..tracking import TrackingScheduledRunner
from .consts import SLEEPS


def test_tracking_basic_schedule(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    q: queue.Queue[int] = queue.Queue()

    # Initially no handles
    assert len(tracker.get_handles()) == 0

    # Schedule a task
    h = tracker.schedule(SLEEPS * 5, lambda: q.put(42))

    # Handle should be tracked
    handles = tracker.get_handles()
    assert len(handles) == 1
    assert h in handles

    # Wait for completion
    assert h.result(timeout=SLEEPS * 100) is None
    assert q.get(timeout=SLEEPS * 100) == 42

    # After completion, handle should be removed from tracking
    time.sleep(SLEEPS * 5)  # Give callback time to run
    assert len(tracker.get_handles()) == 0


def test_tracking_multiple_handles(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    q: queue.Queue[int] = queue.Queue()

    # Schedule multiple tasks with more spacing
    h1 = tracker.schedule(SLEEPS * 5, lambda: q.put(1))
    h2 = tracker.schedule(SLEEPS * 20, lambda: q.put(2))
    h3 = tracker.schedule(SLEEPS * 30, lambda: q.put(3))

    # All should be tracked
    handles = tracker.get_handles()
    assert len(handles) == 3
    assert h1 in handles
    assert h2 in handles
    assert h3 in handles

    # Wait for first to complete
    h1.result(timeout=SLEEPS * 100)
    time.sleep(SLEEPS * 5)

    # Should have 2 remaining
    handles = tracker.get_handles()
    assert len(handles) == 2
    assert h1 not in handles
    assert h2 in handles
    assert h3 in handles

    # Wait for all to complete
    h2.result(timeout=SLEEPS * 100)
    h3.result(timeout=SLEEPS * 100)
    time.sleep(SLEEPS * 5)

    # All should be removed
    assert len(tracker.get_handles()) == 0


def test_tracking_cancelled_task(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    executed = []

    h = tracker.schedule(SLEEPS * 50, lambda: executed.append(True))

    # Should be tracked
    assert len(tracker.get_handles()) == 1

    # Cancel it
    assert h.cancel()
    time.sleep(SLEEPS * 5)

    # Should be removed from tracking after cancellation
    assert len(tracker.get_handles()) == 0
    assert executed == []


def test_cancel_all_handles(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    executed = []

    # Schedule multiple long-running tasks
    h1 = tracker.schedule(SLEEPS * 100, lambda: executed.append(1))
    h2 = tracker.schedule(SLEEPS * 100, lambda: executed.append(2))
    h3 = tracker.schedule(SLEEPS * 100, lambda: executed.append(3))

    # All should be tracked
    assert len(tracker.get_handles()) == 3

    # Cancel all
    tracker.cancel_all_handles()
    time.sleep(SLEEPS * 5)

    # All should be cancelled
    assert h1.cancelled()
    assert h2.cancelled()
    assert h3.cancelled()

    # None should execute
    time.sleep(SLEEPS * 10)
    assert executed == []

    # All should be removed from tracking
    assert len(tracker.get_handles()) == 0


def test_get_handles_returns_copy(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    h1 = tracker.schedule(SLEEPS * 10, lambda: None)  # noqa
    h2 = tracker.schedule(SLEEPS * 10, lambda: None)  # noqa

    # Get handles
    handles1 = tracker.get_handles()
    assert len(handles1) == 2

    # Modify the returned set
    handles1.clear()

    # Original should be unchanged
    handles2 = tracker.get_handles()
    assert len(handles2) == 2


def test_tracking_with_exception(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    def boom():
        raise ValueError('test error')

    h = tracker.schedule(SLEEPS * 5, boom)

    # Should be tracked
    assert len(tracker.get_handles()) == 1

    # Wait for exception
    with pytest.raises(ValueError, match='test error'):
        h.result(timeout=SLEEPS * 100)

    # Should be removed from tracking even with exception
    time.sleep(SLEEPS * 5)
    assert len(tracker.get_handles()) == 0


def test_tracking_concurrent_scheduling(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    results = []
    lock = threading.Lock()
    all_handles = []

    def task(value):
        def fn():
            with lock:
                results.append(value)
            return value
        return fn

    def schedule_tasks(start, count):
        for i in range(start, start + count):
            h = tracker.schedule(SLEEPS * 5, task(i))
            with lock:
                all_handles.append(h)

    # Schedule from multiple threads
    threads = [
        threading.Thread(target=schedule_tasks, args=(0, 10)),
        threading.Thread(target=schedule_tasks, args=(10, 10)),
        threading.Thread(target=schedule_tasks, args=(20, 10)),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All 30 handles should be tracked
    assert len(tracker.get_handles()) == 30

    # Wait for all to complete
    for h in all_handles:
        h.result(timeout=SLEEPS * 100)

    time.sleep(SLEEPS * 10)

    # All should be removed
    assert len(tracker.get_handles()) == 0
    assert len(results) == 30
    assert sorted(results) == list(range(30))


def test_tracking_shutdown_delegates(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    executed = []

    # Schedule a task
    tracker.schedule(SLEEPS * 5, lambda: executed.append(1))

    # Shutdown with cancel_all
    tracker.shutdown(cancel_all=True)

    # Task should not execute
    assert executed == []


def test_tracking_get_state_delegates(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    from ..types import ScheduledRunnerState

    # Initially NEW
    assert tracker.get_state() == ScheduledRunnerState.NEW

    # Schedule a task to start the thread
    tracker.schedule(SLEEPS * 1, lambda: None)

    # Should be RUNNING
    assert tracker.get_state() == ScheduledRunnerState.RUNNING

    # Shutdown
    tracker.shutdown()

    # Should be STOPPED
    assert tracker.get_state() == ScheduledRunnerState.STOPPED


def test_tracking_wait_delegates(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    # Schedule a task to start the thread
    tracker.schedule(SLEEPS * 1, lambda: None)

    # Shutdown but don't wait
    tracker.shutdown(no_wait=True)

    # Wait should work
    tracker.wait(timeout=SLEEPS * 100)

    from ..types import ScheduledRunnerState
    assert tracker.get_state() == ScheduledRunnerState.STOPPED


def test_tracking_mixed_completion_and_cancellation(request):
    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    q: queue.Queue[int] = queue.Queue()

    # Schedule multiple tasks
    h1 = tracker.schedule(SLEEPS * 2, lambda: q.put(1))  # Will complete
    h2 = tracker.schedule(SLEEPS * 50, lambda: q.put(2))   # Will cancel
    h3 = tracker.schedule(SLEEPS * 4, lambda: q.put(3))  # Will complete
    h4 = tracker.schedule(SLEEPS * 50, lambda: q.put(4))   # Will cancel

    assert len(tracker.get_handles()) == 4

    # Cancel some
    h2.cancel()
    h4.cancel()

    # Wait for others to complete
    h1.result(timeout=SLEEPS * 100)
    h3.result(timeout=SLEEPS * 100)

    time.sleep(SLEEPS * 10)

    # All should be removed from tracking
    assert len(tracker.get_handles()) == 0

    # Only h1 and h3 should have executed
    results = []
    while not q.empty():
        results.append(q.get_nowait())
    assert sorted(results) == [1, 3]


def test_tracking_immediate_callback_on_completion(request):
    """Test that handles are tracked even if they complete very quickly."""

    inner = HeapqScheduledRunner()
    tracker = TrackingScheduledRunner(inner)
    request.addfinalizer(tracker.shutdown)

    # Schedule with zero delay
    h = tracker.schedule(0.0, lambda: 42)

    # Should be briefly tracked
    # (This is a bit racy but the handle should be added before scheduling)
    assert h.result(timeout=SLEEPS * 100) == 42

    # After completion, should be removed
    time.sleep(SLEEPS * 5)
    assert len(tracker.get_handles()) == 0
