import functools
import threading
import time  # noqa
import typing as ta


T = ta.TypeVar('T')
T_co = ta.TypeVar('T_co', covariant=True)


##


class ThreadLoopFn(ta.Protocol[T_co]):
    def __call__(self, thread_idx: int, cur_iter: int) -> T_co: ...


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
    thread_died = threading.Event()

    thread_errors_lock = threading.Lock()
    thread_errors: list[tuple[int, int, BaseException]] = []

    cur_iter = -1
    results: list[object] = []

    def abort_barriers() -> None:
        for barrier in (start_barrier, end_barrier):
            try:
                barrier.abort()
            except Exception:  # noqa
                pass

    def record_thread_error(thread_idx: int, exc: BaseException) -> None:
        with thread_errors_lock:
            thread_errors.append((thread_idx, cur_iter, exc))

        thread_died.set()
        should_exit.set()
        abort_barriers()

    def raise_thread_error() -> ta.NoReturn:
        with thread_errors_lock:
            errors = list(thread_errors)

        if not errors:
            raise RuntimeError('Thread loop worker exited unexpectedly')

        if len(errors) == 1:
            thread_idx, err_iter, exc = errors[0]
            raise RuntimeError(f'Thread loop worker {thread_idx} failed during iteration {err_iter}') from exc

        raise RuntimeError(
            f'Multiple thread loop workers failed: ' + ', '.join(
                f'thread {thread_idx} during iteration {err_iter}: {exc!r}'
                for thread_idx, err_iter, exc in errors
            ),
        ) from errors[0][2]

    def thread_main(thread_idx: int) -> None:
        try:
            while True:
                try:
                    start_barrier.wait()
                except threading.BrokenBarrierError:
                    return

                if should_exit.is_set():
                    return

                try:
                    result = thread_fn(thread_idx, cur_iter)
                    results[thread_idx] = result
                except BaseException as exc:  # noqa
                    record_thread_error(thread_idx, exc)
                    return

                try:
                    end_barrier.wait()
                except threading.BrokenBarrierError:
                    return

        finally:
            # If this worker vanishes while the system is not already shutting down, force everyone else out of any
            # barrier waits.
            if not should_exit.is_set():
                thread_died.set()
                should_exit.set()
                abort_barriers()

    threads = [
        threading.Thread(target=functools.partial(thread_main, i))
        for i in range(n_threads)
    ]

    started_threads: list[threading.Thread] = []

    try:
        for thread in threads:
            thread.start()
            started_threads.append(thread)

        not_set = object()

        for cur_iter in range(n_iters):
            results = [not_set] * n_threads

            if thread_died.is_set():
                raise_thread_error()

            if before_fn is not None:
                before_fn(cur_iter)

            try:
                start_barrier.wait()
                end_barrier.wait()
            except threading.BrokenBarrierError:
                if thread_died.is_set():
                    raise_thread_error()
                raise

            if thread_died.is_set():
                raise_thread_error()

            if (not_set_idxs := [i for i, e in enumerate(results) if e is not_set]):
                raise RuntimeError(
                    f'Thread loop did not produce result for iteration {cur_iter} in threads {not_set_idxs}',
                )

            if after_fn is not None:
                after_fn(cur_iter, ta.cast('list[T]', results))  # noqa

    finally:
        should_exit.set()
        abort_barriers()

        for thread in started_threads:
            thread.join()
