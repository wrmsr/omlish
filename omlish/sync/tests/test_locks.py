import queue
import threading
import time

import pytest

from ..locks import AttemptedReentrantAcquireLockError
from ..locks import AttemptedUnownedReleaseLockError
from ..locks import StrictLock


def test_initially_unlocked() -> None:
    lock = StrictLock()

    assert not lock.locked()
    assert lock.owner is None


def test_acquire_and_release() -> None:
    lock = StrictLock()

    assert lock.acquire()
    assert lock.locked()
    assert lock.owner == threading.get_ident()

    lock.release()

    assert not lock.locked()
    assert lock.owner is None


def test_context_manager_acquires_and_releases() -> None:
    lock = StrictLock()

    with lock as entered:
        assert entered is lock
        assert lock.locked()
        assert lock.owner == threading.get_ident()

    assert not lock.locked()
    assert lock.owner is None


def test_reentrant_acquire_raises() -> None:
    lock = StrictLock()

    lock.acquire()
    try:
        with pytest.raises(AttemptedReentrantAcquireLockError):
            lock.acquire()

        assert lock.locked()
        assert lock.owner == threading.get_ident()

    finally:
        lock.release()


def test_reentrant_nonblocking_acquire_raises() -> None:
    lock = StrictLock()

    lock.acquire()
    try:
        with pytest.raises(AttemptedReentrantAcquireLockError):
            lock.acquire(blocking=False)

    finally:
        lock.release()


def test_reentrant_timeout_acquire_raises_immediately() -> None:
    lock = StrictLock()

    lock.acquire()
    try:
        start = time.monotonic()

        with pytest.raises(AttemptedReentrantAcquireLockError):
            lock.acquire(timeout=10)

        assert time.monotonic() - start < 1

    finally:
        lock.release()


def test_release_without_owner_raises() -> None:
    lock = StrictLock()

    with pytest.raises(AttemptedUnownedReleaseLockError):
        lock.release()


def test_release_from_non_owner_thread_raises() -> None:
    lock = StrictLock()
    lock.acquire()

    q: queue.Queue[BaseException | None] = queue.Queue()

    def worker() -> None:
        try:
            lock.release()
        except BaseException as e:  # noqa
            q.put(e)
        else:
            q.put(None)

    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout=5)

    assert not t.is_alive()

    exc = q.get_nowait()
    assert isinstance(exc, AttemptedUnownedReleaseLockError)

    assert lock.locked()
    assert lock.owner == threading.get_ident()

    lock.release()


def test_nonblocking_acquire_returns_false_when_held_by_other_thread() -> None:
    lock = StrictLock()
    lock.acquire()

    q: queue.Queue[bool] = queue.Queue()

    def worker() -> None:
        q.put(lock.acquire(blocking=False))

    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout=5)

    assert not t.is_alive()
    assert q.get_nowait() is False

    assert lock.locked()
    assert lock.owner == threading.get_ident()

    lock.release()


def test_timeout_acquire_returns_false_when_held_by_other_thread() -> None:
    lock = StrictLock()
    lock.acquire()

    q: queue.Queue[tuple[bool, float]] = queue.Queue()

    def worker() -> None:
        start = time.monotonic()
        acquired = lock.acquire(timeout=0.05)
        q.put((acquired, time.monotonic() - start))

    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout=5)

    assert not t.is_alive()

    acquired, elapsed = q.get_nowait()
    assert acquired is False
    assert elapsed >= 0.04

    assert lock.locked()
    assert lock.owner == threading.get_ident()

    lock.release()


def test_other_thread_can_acquire_after_release() -> None:
    lock = StrictLock()

    lock.acquire()

    started = threading.Event()
    acquired = threading.Event()
    done = threading.Event()

    def worker() -> None:
        started.set()
        with lock:
            acquired.set()
            assert lock.owner == threading.get_ident()
        done.set()

    t = threading.Thread(target=worker)
    t.start()

    assert started.wait(timeout=5)
    assert not acquired.wait(timeout=0.05)

    lock.release()

    assert acquired.wait(timeout=5)
    assert done.wait(timeout=5)

    t.join(timeout=5)
    assert not t.is_alive()

    assert not lock.locked()
    assert lock.owner is None


def test_exception_inside_context_still_releases() -> None:
    lock = StrictLock()

    with pytest.raises(ValueError):  # noqa
        with lock:
            assert lock.locked()
            raise ValueError('boom')

    assert not lock.locked()
    assert lock.owner is None


def test_repr_smoke() -> None:
    lock = StrictLock()

    assert 'StrictLock' in repr(lock)
    assert 'unlocked' in repr(lock)

    with lock:
        assert 'locked' in repr(lock)
        assert str(threading.get_ident()) in repr(lock)
