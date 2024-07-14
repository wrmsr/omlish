import contextlib
import threading

from .. import impl
from .. import proxy
from ...threading import CountDownLatch


def test_proxy():
    class C:

        def __init__(self):
            self.calls = []

        def f(self, a):
            self.calls.append(a)
            return a + 1

    c = C()
    assert c.f(1) == 2

    PC = proxy.make_suspending_proxy(['f'])
    pc = PC(c)
    assert pc.f(2) == 3
    assert c.f(3) == 4
    assert pc.f(4) == 5

    assert c.calls == [1, 2, 3, 4]


def test_dump():
    with impl.WatchdogImpl() as wd:
        wd._reporter.report_violations(wd, set(), set())


def test_thread_current():
    class Obj:
        pass

    def thread_proc(n):
        watches = watches_by_thread[threading.current_thread()] = []
        with contextlib.ExitStack() as es:
            objs = []
            for i in range(n):
                obj = Obj()
                objs.append(obj)
                watches.append(es.enter_context(wd.watch(obj)))

            currents_by_thread[threading.current_thread()] = wd.thread_current

            latch.count_down()
            latch.wait()

            shutdown_event.wait()

    num_watches = 50
    num_threads = 64

    watches_by_thread = {}
    currents_by_thread = {}

    latch = CountDownLatch(num_threads)
    shutdown_event = threading.Event()
    with impl.WatchdogImpl(
            shutdown_event=shutdown_event,
            config=impl.WatchdogImpl.Config(
                threshold=0.5,
            ),
    ) as wd:
        threads = [threading.Thread(target=lambda: thread_proc(num_watches)) for _ in range(num_threads)]
        for thread in threads:
            thread.start()
        latch.wait()

        for thread in threads:
            assert len(watches_by_thread[thread]) == num_watches
            assert set(currents_by_thread[thread]) == set(watches_by_thread[thread])

        shutdown_event.set()
        for thread in threads:
            thread.join()
