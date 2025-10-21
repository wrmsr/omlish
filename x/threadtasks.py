# ruff: noqa: UP006 UP045
# @omlish-lite
"""
TODO:
 - errors lol - set fut.error
 - winch down relay tasks?
 - logging i guess
 - shutting down flag, dont submit more work
"""
import asyncio
import dataclasses as dc
import queue
import sys
import threading
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check


##


class ThreadTasks:
    def __init__(
            self,
            *,
            num_workers: ta.Optional[int] = None,
            max_relays: ta.Optional[int] = None,
            loop: ta.Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        super().__init__()

        if num_workers is None:
            num_workers = self._get_num_cpus() or self._DEFAULT_NUM_WORKERS
        check.arg(num_workers > 0)
        self._num_workers = num_workers
        self._max_relays = max_relays

        #

        self._loop = loop or asyncio.get_running_loop()

        self._tasks: ta.Set[ThreadTasks._Task] = set()

        self._relay_queue: asyncio.Queue[ThreadTasks._RelayMessage] = asyncio.Queue()
        self._relays: ta.Set[ThreadTasks._Relay] = set()

        self._worker_queue: queue.Queue[ThreadTasks._WorkerMessage] = queue.Queue()
        self._workers: ta.List[ThreadTasks._Worker] = [
            self._Worker(
                self,
                i,
            )
            for i in range(num_workers)
        ]

    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}@{id(self):x}'

    #

    _DEFAULT_NUM_WORKERS: ta.ClassVar[int] = 2

    @classmethod
    def _get_num_cpus(cls) -> ta.Optional[int]:
        if sys.version_info >= (3, 13):  # noqa: UP036
            import os
            return os.cpu_count()
        else:
            import multiprocessing as mp
            return mp.cpu_count()

    #

    class _Task:
        def __init__(
                self,
                coro: ta.Coroutine,
                result: asyncio.Future,
        ) -> None:
            super().__init__()

            self.coro = coro
            self.result = result

        awa: ta.Any = None
        gen: ta.Any = None

        fut: ta.Optional['ThreadTasks._Future'] = None

        def close(self) -> None:
            if (g := self.gen) is not None:
                g.close()

            if (a := self.awa) is not None:
                a.close()

            self.coro.close()

        def run(self) -> ta.Optional['ThreadTasks._RelayMessage']:
            if (f := self.fut) is not None:
                return ThreadTasks._SubmitFuture(f)

            if (a := self.awa) is None:
                a = self.awa = self.coro.__await__()

            if (g := self.gen) is None:
                g = self.gen = iter(a)

            try:
                f = g.send(None)
            except StopIteration as se:
                self.close()
                return ThreadTasks._SubmitResult(self, result=se.value)

            if isinstance(f, ThreadTasks._Future):
                try:
                    f.task  # noqa: B018
                except AttributeError:
                    pass
                else:
                    raise RuntimeError
                f.task = self
                return ThreadTasks._SubmitFuture(f)

            else:
                raise TypeError(f)

    #

    class _Future:
        def __init__(self, fn: ta.Callable[[], ta.Awaitable]) -> None:
            super().__init__()

            self.fn = fn

        task: 'ThreadTasks._Task'

        done: bool = False
        result: ta.Any
        error: ta.Optional[BaseException] = None

        def __await__(self) -> ta.Generator[ta.Any, None, ta.Any]:
            if not self.done:
                yield self
            if not self.done:
                raise RuntimeError
            if self.error is not None:
                raise self.error
            else:
                return self.result

    #

    class _WorkerMessage(Abstract):
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class _RunTask(_WorkerMessage):
        task: 'ThreadTasks._Task'

    @ta.final
    class _ShutdownWorker(_WorkerMessage):
        pass

    class _Worker:
        def __init__(
                self,
                owner: 'ThreadTasks',
                worker_idx: int,
        ) -> None:
            super().__init__()

            self.owner = owner
            self.worker_idx = worker_idx

            self.thread = ThreadTasks._Worker._Thread(  # noqa: SLF001
                _thread_tasks_worker=self,
                target=self._worker_main,
                name=repr(self),
            )

        class _Thread(threading.Thread):
            def __init__(
                    self,
                    *args: ta.Any,
                    _thread_tasks_worker: 'ThreadTasks._Worker',
                    **kwargs: ta.Any,
            ) -> None:
                super().__init__(*args, **kwargs)

                self._thread_tasks_worker = _thread_tasks_worker

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}@{id(self):x}(owner={self.owner!r}, worker_idx={self.worker_idx!r})'

        def _worker_main(self) -> None:
            while True:
                w_msg = self.owner._worker_queue.get()  # noqa: SLF001

                try:
                    if isinstance(w_msg, ThreadTasks._RunTask):
                        if (r_msg := w_msg.task.run()) is not None:
                            self.owner._relay(r_msg)  # noqa: SLF001

                    elif isinstance(w_msg, ThreadTasks._ShutdownWorker):
                        break

                    else:
                        raise TypeError(w_msg)

                finally:
                    self.owner._worker_queue.task_done()  # noqa: SLF001

    #

    class _RelayMessage(Abstract):
        pass

    @ta.final
    @dc.dataclass()
    class _SubmitFuture(_RelayMessage):
        fut: 'ThreadTasks._Future'

    @ta.final
    @dc.dataclass()
    class _SubmitResult(_RelayMessage):
        task: 'ThreadTasks._Task'

        # _: dc.KW_ONLY

        result: ta.Any = None
        error: ta.Optional[BaseException] = None

    @ta.final
    class _ShutdownRelay(_RelayMessage):
        pass

    class _Relay:
        def __init__(
                self,
                owner: 'ThreadTasks',
        ) -> None:
            super().__init__()

            self.owner = owner

            self.task = owner._loop.create_task(  # noqa: SLF001
                self._relay_main(),
                name=repr(self),
            )

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}@{id(self):x}(owner={self.owner!r})'

        task: asyncio.Task

        async def _relay_main(self) -> None:
            while True:
                msg = await self.owner._relay_queue.get()  # noqa: SLF001

                try:
                    if isinstance(msg, ThreadTasks._SubmitFuture):
                        try:
                            a = msg.fut.fn()
                            v = await a
                        except BaseException as e:  # noqa: BLE001
                            msg.fut.error = e
                        else:
                            msg.fut.result = v
                        msg.fut.done = True

                        self.owner._worker_queue.put(ThreadTasks._RunTask(msg.fut.task))  # noqa: SLF001

                    elif isinstance(msg, ThreadTasks._SubmitResult):  # noqa: SLF001
                        msg.task.result.set_result(msg.result)
                        self.owner._tasks.remove(msg.task)  # noqa: SLF001

                    elif isinstance(msg, ThreadTasks._ShutdownRelay):  # noqa: SLF001
                        break

                    else:
                        raise TypeError(msg)

                finally:
                    self.owner._relay_queue.task_done()  # noqa: SLF001

    def _relay(self, msg: _RelayMessage) -> None:
        async def inner():
            if (
                isinstance(msg, ThreadTasks._SubmitFuture) and
                (
                    not self._relays or
                    self._relay_queue.qsize()
                ) and
                (
                    self._max_relays is None or
                    len(self._relays) < self._max_relays
                )
            ):
                self._relays.add(self._Relay(self))

            await self._relay_queue.put(msg)

        asyncio.run_coroutine_threadsafe(inner(), self._loop)

    #

    async def start(self) -> None:
        for w in self._workers:
            w.thread.start()

    async def shutdown(self) -> None:
        for _ in range(len(self._workers)):
            self._worker_queue.put(ThreadTasks._ShutdownWorker())
        for w in self._workers:
            w.thread.join()

        for _ in range(len(self._relays)):
            await self._relay_queue.put(ThreadTasks._ShutdownRelay())
        for r in self._relays:
            await r.task

    #

    class Handle:
        def __init__(
                self,
                *,
                _task: 'ThreadTasks._Task',
                _result: asyncio.Future,
        ) -> None:
            super().__init__()

            self._task = _task
            self._result = _result

        def __await__(self):
            return self._result.__await__()

    async def spawn(self, fn: ta.Callable[[], ta.Coroutine]) -> Handle:
        coro = fn()
        result = self._loop.create_future()
        task = self._Task(coro, result)
        handle = self.Handle(_task=task, _result=result)
        self._tasks.add(task)
        self._worker_queue.put(ThreadTasks._RunTask(task))
        return handle


def thread_await(fn: ta.Callable[[], ta.Awaitable]) -> ta.Awaitable[ta.Any]:
    return ThreadTasks._Future(fn)  # noqa


##


async def _a_main() -> None:
    import random
    import time

    #

    say_lock = threading.Lock()
    say_st = time.time()

    def say(task_idx: int, msg: str) -> None:
        worker_idx = threading.current_thread()._thread_tasks_worker.worker_idx  # type: ignore  # noqa
        with say_lock:
            print(
                f'time {format(time.time() - say_st, ".2f"):>6} : '
                f'worker {worker_idx} : '
                f'task {task_idx} : '
                f'{msg}',
                flush=True,
            )

    #

    def sleep_time() -> float:
        return (random.random() * .5) + .5

    #

    spin_its = 10_000

    def _spin() -> None:
        c = 0
        for _ in range(spin_its):
            c += 1  # noqa: SIM113

    def calc_spin_rate() -> int:
        et = time.time() + 1
        c = 0
        while time.time() < et:
            _spin()
            c += 1
        return c

    spin_rate = calc_spin_rate()

    spin_lock = threading.Lock()
    spin_time = 0.

    def spin_for(st: float) -> None:
        bt = time.time()
        for _ in range(int(st * spin_rate)):
            _spin()
        et = time.time() - bt
        with spin_lock:
            nonlocal spin_time
            spin_time += et

    #

    async def work(idx: int) -> int:
        say(idx, f'start')

        for i in range(4):
            st = sleep_time()
            say(idx, f'asleep {i} : start {st:.2}')
            await thread_await(lambda: asyncio.sleep(st))  # noqa: B023
            say(idx, f'asleep {i} : end   {st:.2}')

            st = sleep_time()
            say(idx, f'spin   {i} : start {st:.2}')
            spin_for(st)
            say(idx, f'spin   {i} : end   {st:.2}')

        say(idx, f'end')
        return idx

    #

    tts = ThreadTasks(num_workers=2)
    await tts.start()

    run_st = time.time()
    futs = [await (lambda i: tts.spawn(lambda: work(i)))(i) for i in range(4)]  # noqa: PLC3002
    for fut in futs:
        print(await fut)
    run_et = time.time() - run_st

    print(f'run time: {run_et:.2f}')
    print(f'spin time: {spin_time:.2f}')

    await tts.shutdown()


if __name__ == '__main__':
    asyncio.run(_a_main())
