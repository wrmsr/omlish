"""
** DO NOT USE LOL - currently for demonstration purposes only, may be built up later **

====

Hashed Wheel Timer implementation.

A time-wheel scheduler with O(1) insertion and cancellation, at the cost of quantized time resolution.

Based on Varghese & Lauck's "Hashed and Hierarchical Timing Wheels" (1987).

====

TODO:
 - Hybridize? Want sleep/wake
"""
import dataclasses as dc
import threading  # noqa
import time

from .base import BaseScheduledRunner
from .handles import ScheduleHandleImpl
from .types import ScheduledFn
from .types import ScheduledRunnerState
from .types import ScheduleHandle


##


class HwtScheduledRunner(BaseScheduledRunner):
    """
    Hashed wheel timer for scheduling tasks.

    - O(1) insertion and cancellation
    - Fixed tick duration (default 10ms)
    - Time resolution quantized to tick duration
    - Thread-safe
    """

    def __init__(
        self,
        *,
        tick_duration: float = 0.01,  # 10ms
        wheel_size: int = 512,
    ) -> None:
        super().__init__()

        self._tick_duration = tick_duration
        self._wheel_size = wheel_size

        self._wheel: list[list[HwtScheduledRunner._Task]] = [[] for _ in range(wheel_size)]
        self._current_tick = 0
        self._task_map: dict[ScheduleHandleImpl, HwtScheduledRunner._Task] = {}
        self._thread: threading.Thread | None = None

    @dc.dataclass()
    class _Task:
        deadline: float  # absolute monotonic time
        fn: ScheduledFn
        handle: ScheduleHandleImpl

        rounds: int  # number of wheel rotations to wait

    def schedule(self, delay: float, fn: ScheduledFn) -> ScheduleHandle:
        deadline = time.monotonic() + max(0.0, float(delay))

        with self._cv:
            self._ensure_thread_locked()
            self._check_state(ScheduledRunnerState.RUNNING)

            # Calculate ticks from now
            ticks = int(delay / self._tick_duration)
            rounds = ticks // self._wheel_size
            bucket = (self._current_tick + ticks) % self._wheel_size

            h = ScheduleHandleImpl(self._cv)

            task = HwtScheduledRunner._Task(
                deadline=deadline,
                fn=fn,
                handle=h,
                rounds=rounds,
            )

            self._wheel[bucket].append(task)
            self._task_map[h] = task

            return h

    def _thread_main(self) -> None:
        cancel: list[ScheduleHandle] | None = None

        next_tick_time = time.monotonic()

        while True:
            next_tick_time += self._tick_duration
            sleep_duration = next_tick_time - time.monotonic()

            if sleep_duration > 0:
                time.sleep(sleep_duration)

            tasks_to_run: list[HwtScheduledRunner._Task] = []

            with self._cv:
                # FIXME: draining
                if self._state != ScheduledRunnerState.RUNNING:
                    break

                # Get next tasks

                # Get tasks from current bucket
                bucket = self._wheel[self._current_tick]
                remaining: list[HwtScheduledRunner._Task] = []

                for task in bucket:
                    # Skip cancelled/done tasks
                    if task.handle.done():
                        # Remove from tracking map
                        self._task_map.pop(task.handle, None)
                        continue

                    if task.rounds > 0:
                        # Not ready yet, decrement rounds and keep in bucket
                        task.rounds -= 1
                        remaining.append(task)
                    else:
                        # Ready to run
                        tasks_to_run.append(task)
                        self._task_map.pop(task.handle, None)
                        task.handle._set_running()  # noqa

                # Replace bucket with remaining tasks
                self._wheel[self._current_tick] = remaining

                # Advance tick
                self._current_tick = (self._current_tick + 1) % self._wheel_size

            # Execute tasks without lock
            for task in tasks_to_run:
                self._run_task(task)

        if cancel:
            for t in cancel:
                t.cancel()

    def _run_task(self, task: _Task) -> None:
        if task.handle.cancelled():
            return

        try:
            res = task.fn()
        except BaseException as e:  # noqa
            task.handle._set_exception(e)  # noqa
        else:
            task.handle._set_result(res)  # noqa
