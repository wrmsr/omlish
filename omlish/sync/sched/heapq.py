import dataclasses as dc
import heapq
import itertools
import time

from ... import check
from .base import BaseScheduledRunner
from .handles import ScheduleHandleImpl
from .types import ScheduledFn
from .types import ScheduledRunnerState
from .types import ScheduledRunnerStateError
from .types import ScheduleHandle


##


class HeapqScheduledRunner(BaseScheduledRunner):
    """
    Single-thread scheduled executor.

    - Uses time.monotonic()
    - Executes fn in the runner thread (keep it non-blocking)
    - Thread-safe
    """

    def __init__(
            self,
            *,
            batch_size: int | None = None,
            batch_max_time_s: float | None = None,
    ) -> None:
        super().__init__()

        if batch_size is None:
            batch_size = 1
        if not (batch_size > 0):
            raise ValueError('batch_size must be positive')
        self._batch_size = batch_size
        self._batch_max_time_s = batch_max_time_s

        self._heap: list[tuple[float, int, HeapqScheduledRunner._Task]] = []

    _seq = 0

    @dc.dataclass()
    class _Task:
        when: float
        seq: int
        fn: ScheduledFn
        handle: 'ScheduleHandleImpl'

        running: bool = False

    def schedule(self, delay: float, fn: ScheduledFn) -> ScheduleHandle:
        when = time.monotonic() + max(0., delay)

        with self._cv:
            self._ensure_thread_locked()
            self._check_state(ScheduledRunnerState.RUNNING)

            self._seq += 1

            h = ScheduleHandleImpl(self._cv)

            task = HeapqScheduledRunner._Task(
                when=when,
                seq=self._seq,
                fn=fn,
                handle=h,
            )

            heapq.heappush(self._heap, (task.when, task.seq, task))

            # Wake if this is the earliest task
            if self._heap[0][2] is task:
                self._cv.notify()

            return h

    def _thread_main(self) -> None:
        recycle: list[HeapqScheduledRunner._Task] | None = None
        cancel: list[ScheduleHandle] | None = None

        for epoch in itertools.count():  # noqa
            popped: HeapqScheduledRunner._Task | list[HeapqScheduledRunner._Task] | None = None

            with self._cv:
                # Recycle unhandled popped tasks from last iteration

                if recycle:
                    for t in recycle:
                        check.state(not t.running)
                        heapq.heappush(self._heap, (t.when, t.seq, t))
                    recycle = None

                # Skip cancelled/done tasks at heap head

                while self._heap:
                    _when, _seq, t = self._heap[0]
                    if not t.handle.done():
                        break
                    heapq.heappop(self._heap)

                # Check state

                if self._state == ScheduledRunnerState.RUNNING:
                    pass

                elif self._state == ScheduledRunnerState.STOPPING:
                    cancel = []
                    for _, _, t in self._heap:
                        check.state(not t.running)
                        cancel.append(t.handle)
                    self._heap.clear()
                    break

                elif self._state == ScheduledRunnerState.DRAINING:
                    if not self._heap:
                        break

                else:
                    raise ScheduledRunnerStateError(self._state)

                # Wait for runnable heap

                if not self._heap:
                    self._cv.wait()
                    continue

                now = time.monotonic()

                when, _seq, t = self._heap[0]
                check.state(not t.running)
                if when > now:
                    self._cv.wait(timeout=(when - now))
                    continue

                # Pop task chunk

                n = 0
                while n < self._batch_size and self._heap:
                    when, _seq, t = self._heap[0]
                    check.state(not t.running)
                    if when > now:
                        break

                    heapq.heappop(self._heap)
                    if t.handle.done():
                        continue

                    if not n:
                        popped = t
                    elif n == 1:
                        popped = [popped, t]  # type: ignore
                    else:
                        popped.append(t)  # type: ignore

                    n += 1

            # Run popped tasks

            if n == 1:
                self._run_task(popped)  # type: ignore

            elif n > 1:
                if (bmt := self._batch_max_time_s) is not None:
                    deadline: float | None = now + bmt
                else:
                    deadline = None

                i = 0
                for t in popped:  # type: ignore
                    i += 1
                    self._run_task(t)
                    if deadline is not None and time.monotonic() >= deadline:
                        break

                if i < len(popped):  # type: ignore
                    recycle = popped[i:]  # type: ignore

        if cancel:
            for h in cancel:
                h.cancel()

    def _run_task(self, task: _Task) -> None:
        check.state(not task.running)
        task.running = True
        task.handle._set_running()  # noqa

        # execute without lock
        if task.handle.cancelled():
            return

        try:
            res = task.fn()
        except BaseException as e:  # noqa
            task.handle._set_exception(e)  # noqa
        else:
            task.handle._set_result(res)  # noqa
        finally:
            task.running = False
