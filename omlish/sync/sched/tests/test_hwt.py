import threading
import time

import pytest

from ..hwt import HwtScheduledRunner
from ..types import ScheduledCancelledError
from ..types import ScheduledRunnerStateError
from ..types import ScheduledTimeoutError
from .consts import SLEEPS


def test_basic_schedule(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    result = []

    def task():
        result.append(42)
        return 42

    handle = timer.schedule(SLEEPS * 5, task)

    # Should not be done immediately
    assert not handle.done()

    # Wait for completion
    assert handle.result(timeout=SLEEPS * 100) == 42
    assert handle.done()
    assert result == [42]

    timer.shutdown()


def test_cancel_all_schedule(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    executed = []

    def task():
        executed.append(True)
        return 'done'

    handle = timer.schedule(0, task)

    assert handle.result(timeout=SLEEPS * 100) == 'done'
    assert executed == [True]

    timer.shutdown()


def test_cancel_before_execution(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    executed = []

    def task():
        executed.append(True)

    handle = timer.schedule(SLEEPS * 50, task)

    # Cancel immediately
    assert handle.cancel()
    assert handle.cancelled()
    assert handle.done()

    # Should not execute
    time.sleep(SLEEPS * 60)
    assert executed == []

    # result() should raise
    with pytest.raises(ScheduledCancelledError):
        handle.result()

    timer.shutdown()


def test_cancel_returns_false_if_running(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    event = threading.Event()

    def task():
        event.wait()
        return 'done'

    handle = timer.schedule(SLEEPS * 2, task)

    # Wait for task to start
    time.sleep(SLEEPS * 5)
    assert handle.running()

    # Cancel should fail while running
    assert not handle.cancel()

    # Let task complete
    event.set()
    handle.result(timeout=SLEEPS * 100)

    # Cancel should fail after done
    assert not handle.cancel()

    timer.shutdown()


def test_exception_in_task(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    def task():
        raise ValueError('test error')

    handle = timer.schedule(SLEEPS * 5, task)

    with pytest.raises(ValueError, match='test error'):
        handle.result(timeout=SLEEPS * 100)

    assert handle.done()
    assert isinstance(handle.exception(timeout=SLEEPS * 10), ValueError)

    timer.shutdown()


def test_multiple_tasks(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    results = []

    def make_task(value):
        def task():
            results.append(value)
            return value
        return task

    handles = [
        timer.schedule(SLEEPS * 2, make_task(1)),
        timer.schedule(SLEEPS * 5, make_task(2)),
        timer.schedule(SLEEPS * 8, make_task(3)),
    ]

    # Wait for all
    for h in handles:
        h.result(timeout=SLEEPS * 100)

    # All should have executed
    assert results == [1, 2, 3]

    timer.shutdown()


def test_wheel_rotation(request):
    # Small wheel to force multiple rotations
    timer = HwtScheduledRunner(tick_duration=SLEEPS * 1, wheel_size=10)
    request.addfinalizer(timer.shutdown)

    result = []

    def task():
        result.append('done')
        return 'done'

    # Schedule beyond one rotation: 10 buckets * SLEEPS = SLEEPS * 10 per rotation
    # SLEEPS * 25 = 2.5 rotations
    handle = timer.schedule(SLEEPS * 25, task)

    assert handle.result(timeout=SLEEPS * 100) == 'done'
    assert result == ['done']

    timer.shutdown()


def test_done_callback(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    callback_results = []

    def task():
        return 42

    def callback(handle):
        callback_results.append(handle.result())

    handle = timer.schedule(SLEEPS * 5, task)
    handle.add_done_callback(callback)

    handle.result(timeout=SLEEPS * 100)

    # Give callback time to run
    time.sleep(SLEEPS * 5)

    assert callback_results == [42]

    timer.shutdown()


def test_done_callback_cancel_all(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    callback_results = []

    def task():
        return 42

    def callback(handle):
        callback_results.append('called')

    handle = timer.schedule(SLEEPS * 2, task)
    handle.result(timeout=SLEEPS * 100)

    # Add callback after completion - should invoke immediately
    handle.add_done_callback(callback)

    assert callback_results == ['called']

    timer.shutdown()


def test_result_timeout(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
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
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    # Schedule one task to start the thread
    timer.schedule(SLEEPS * 10, lambda: None)

    # Shutdown
    timer.shutdown(no_wait=True)

    # Try to schedule new task
    with pytest.raises(ScheduledRunnerStateError):
        timer.schedule(SLEEPS * 10, lambda: 42)


def test_concurrent_scheduling(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    results = []
    lock = threading.Lock()

    def task(value):
        def fn():
            with lock:
                results.append(value)
            return value
        return fn

    # Schedule from multiple threads
    handles = []

    def schedule_tasks(start, count):
        for i in range(start, start + count):
            h = timer.schedule(SLEEPS * 5, task(i))
            with lock:
                handles.append(h)

    threads = [
        threading.Thread(target=schedule_tasks, args=(0, 10)),
        threading.Thread(target=schedule_tasks, args=(10, 10)),
        threading.Thread(target=schedule_tasks, args=(20, 10)),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Wait for all tasks
    for h in handles:
        h.result(timeout=SLEEPS * 100)

    assert len(results) == 30
    assert sorted(results) == list(range(30))

    timer.shutdown()


def test_status_methods(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    event = threading.Event()

    def task():
        event.wait()
        return 42

    handle = timer.schedule(SLEEPS * 2, task)

    # Initially not done, not cancelled, not running
    assert not handle.done()
    assert not handle.cancelled()
    assert not handle.running()

    # Wait for running
    time.sleep(SLEEPS * 5)
    assert handle.running()
    assert not handle.done()

    # Complete the task
    event.set()
    handle.result(timeout=SLEEPS * 100)

    assert handle.done()
    assert not handle.running()
    assert not handle.cancelled()

    timer.shutdown()


def test_precision(request):
    timer = HwtScheduledRunner(tick_duration=SLEEPS)
    request.addfinalizer(timer.shutdown)

    start = time.monotonic()

    def task():
        return time.monotonic()

    handle = timer.schedule(SLEEPS * 10, task)
    result_time = handle.result(timeout=SLEEPS * 100)

    elapsed = result_time - start

    # Should execute around SLEEPS * 10, allow some margin for quantization + scheduling
    assert (SLEEPS * 8) <= elapsed <= (SLEEPS * 15)

    timer.shutdown()
