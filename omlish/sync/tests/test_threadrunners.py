import threading
import time
import typing as ta

import pytest

from ..threadrunners import QueueThreadRunner
from ..threadrunners import SingleThreadRunner
from ..threadrunners import ThreadRunnerClosedError


class TestSingleThreadRunner:
    def test_run_returns_value(self) -> None:
        with SingleThreadRunner() as r:
            assert r.run(lambda: 123) == 123

    def test_run_reraises_exception(self) -> None:
        with SingleThreadRunner() as r:
            with pytest.raises(ValueError, match='boom'):
                r.run(lambda: (_ for _ in ()).throw(ValueError('boom')))

    def test_runs_on_background_thread(self) -> None:
        with SingleThreadRunner() as r:
            caller_tid = threading.get_ident()
            worker_tid = r.run(threading.get_ident)

            assert worker_tid != caller_tid

    def test_reuses_same_background_thread(self) -> None:
        with SingleThreadRunner() as r:
            t0 = r.run(threading.get_ident)
            t1 = r.run(threading.get_ident)

            assert t0 == t1

    def test_serializes_concurrent_callers(self) -> None:
        with SingleThreadRunner() as r:
            entered = threading.Event()
            release = threading.Event()
            results: list[int] = []

            def slow() -> int:
                entered.set()
                release.wait(timeout=1.0)
                return 1

            def fast() -> int:
                return 2

            def t0_fn() -> None:
                results.append(r.run(slow))

            def t1_fn() -> None:
                entered.wait(timeout=1.0)
                results.append(r.run(fast))

            t0 = threading.Thread(target=t0_fn)
            t1 = threading.Thread(target=t1_fn)

            t0.start()
            assert entered.wait(timeout=1.0)
            t1.start()

            time.sleep(0.05)
            assert results == []

            release.set()
            t0.join(timeout=1.0)
            t1.join(timeout=1.0)

            assert sorted(results) == [1, 2]

    def test_close_before_first_run(self) -> None:
        r = SingleThreadRunner()
        r.close()

        with pytest.raises(ThreadRunnerClosedError):
            r.run(lambda: 1)

    def test_close_after_run_prevents_further_runs(self) -> None:
        r = SingleThreadRunner()
        assert r.run(lambda: 1) == 1

        r.close()

        with pytest.raises(ThreadRunnerClosedError):
            r.run(lambda: 2)

    def test_close_is_idempotent(self) -> None:
        r = SingleThreadRunner()
        assert r.run(lambda: 1) == 1

        r.close()
        r.close()


class TestQueueThreadRunner:
    def test_run_returns_value(self) -> None:
        with QueueThreadRunner() as r:
            assert r.run(lambda: 123) == 123

    def test_run_passes_args_and_kwargs(self) -> None:
        with QueueThreadRunner() as r:
            def f(x: int, y: int, *, z: int) -> int:
                return x + y + z

            assert r.run(f, 1, 2, z=3) == 6

    def test_run_reraises_exception(self) -> None:
        with QueueThreadRunner() as r:
            def f() -> ta.NoReturn:
                raise ValueError('boom')

            with pytest.raises(ValueError, match='boom'):
                r.run(f)

    def test_runs_on_background_thread(self) -> None:
        with QueueThreadRunner() as r:
            caller_tid = threading.get_ident()
            worker_tid = r.run(threading.get_ident)

            assert worker_tid != caller_tid

    def test_reuses_same_background_thread(self) -> None:
        with QueueThreadRunner() as r:
            t0 = r.run(threading.get_ident)
            t1 = r.run(threading.get_ident)

            assert t0 == t1

    def test_concurrent_calls_all_complete(self) -> None:
        with QueueThreadRunner() as r:
            started = threading.Event()
            release = threading.Event()
            out: list[int] = []
            out_lock = threading.Lock()

            def slow() -> int:
                started.set()
                assert release.wait(1.0)
                return 1

            def fast(n: int) -> int:
                return n

            def run_slow() -> None:
                v = r.run(slow)
                with out_lock:
                    out.append(v)

            def run_fast(n: int) -> None:
                v = r.run(fast, n)
                with out_lock:
                    out.append(v)

            t0 = threading.Thread(target=run_slow)
            t1 = threading.Thread(target=run_fast, args=(2,))
            t2 = threading.Thread(target=run_fast, args=(3,))

            t0.start()
            assert started.wait(1.0)

            t1.start()
            t2.start()

            time.sleep(0.05)
            with out_lock:
                assert out == []

            release.set()

            t0.join(1.0)
            t1.join(1.0)
            t2.join(1.0)

            assert not t0.is_alive()
            assert not t1.is_alive()
            assert not t2.is_alive()

            assert sorted(out) == [1, 2, 3]

    def test_close_before_first_run(self) -> None:
        r = QueueThreadRunner()
        r.close()

        with pytest.raises(ThreadRunnerClosedError):
            r.run(lambda: 1)

    def test_close_after_run_prevents_further_runs(self) -> None:
        r = QueueThreadRunner()
        try:
            assert r.run(lambda: 1) == 1
        finally:
            r.close()

        with pytest.raises(ThreadRunnerClosedError):
            r.run(lambda: 2)

    def test_close_is_idempotent(self) -> None:
        r = QueueThreadRunner()
        assert r.run(lambda: 1) == 1

        r.close(wait=True)
        r.close(wait=True)

    def test_close_wait_true_waits_for_running_work(self) -> None:
        r = QueueThreadRunner()
        done = threading.Event()

        def slow() -> int:
            time.sleep(0.1)
            done.set()
            return 1

        t = threading.Thread(target=lambda: r.run(slow))
        t.start()

        time.sleep(0.02)
        r.close(wait=True, timeout=1.0)

        t.join(1.0)
        assert done.is_set()
        assert not t.is_alive()

    def test_close_does_not_drop_already_queued_work(self) -> None:
        r = QueueThreadRunner()

        entered = threading.Event()
        release = threading.Event()
        out: list[int] = []
        out_lock = threading.Lock()

        def slow() -> int:
            entered.set()
            assert release.wait(1.0)
            return 1

        def fast() -> int:
            return 2

        def run_and_store(fn) -> None:
            v = r.run(fn)
            with out_lock:
                out.append(v)

        t0 = threading.Thread(target=run_and_store, args=(slow,))
        t1 = threading.Thread(target=run_and_store, args=(fast,))

        t0.start()
        assert entered.wait(1.0)

        t1.start()
        time.sleep(0.05)

        r.close(wait=False)
        release.set()

        t0.join(1.0)
        t1.join(1.0)

        assert not t0.is_alive()
        assert not t1.is_alive()
        assert sorted(out) == [1, 2]

    def test_close_wait_false_returns_without_waiting(self) -> None:
        r = QueueThreadRunner()
        entered = threading.Event()
        release = threading.Event()

        def slow() -> int:
            entered.set()
            assert release.wait(1.0)
            return 1

        t = threading.Thread(target=lambda: r.run(slow))
        t.start()

        assert entered.wait(1.0)

        start = time.monotonic()
        r.close(wait=False)
        elapsed = time.monotonic() - start

        assert elapsed < 0.5

        release.set()
        t.join(1.0)
        assert not t.is_alive()
