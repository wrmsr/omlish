import functools
import threading
import time  # noqa
import typing as ta


T = ta.TypeVar('T')


##


class ThreadLoopFn(ta.Protocol[T]):
    def __call__(self, thread_idx: int, cur_iter: int) -> T: ...


class ThreadLoopBeforeFn(ta.Protocol):
    def __call__(self, cur_iter: int) -> None: ...


class ThreadLoopAfterFn(ta.Protocol[T]):
    def __call__(self, cur_iter: int, results: list[T]) -> None: ...


def run_thread_loops(
        n_threads: int,
        n_iters: int,
        thread_fn: ThreadLoopFn[T],
        *,
        before_fn: ThreadLoopBeforeFn | None = None,
        after_fn: ThreadLoopAfterFn[T] | None = None,
) -> None:
    start_barrier = threading.Barrier(n_threads + 1)
    end_barrier = threading.Barrier(n_threads + 1)

    should_exit = threading.Event()

    cur_iter: int
    results: list[T]

    def thread_main(thread_idx: int) -> None:
        while True:
            start_barrier.wait()

            if should_exit.is_set():
                return

            result = thread_fn(thread_idx, cur_iter)

            results[thread_idx] = result

            end_barrier.wait()

    threads = [
        threading.Thread(target=functools.partial(thread_main, i))
        for i in range(n_threads)
    ]

    for thread in threads:
        thread.start()

    for cur_iter in range(n_iters):
        results = [None] * n_threads

        if before_fn is not None:
            before_fn(cur_iter)

        start_barrier.wait()

        end_barrier.wait()

        if after_fn is not None:
            after_fn(cur_iter, results)

    should_exit.set()
    start_barrier.wait()

    for thread in threads:
        thread.join()
