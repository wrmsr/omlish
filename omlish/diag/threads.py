import io
import itertools
import os
import signal
import sys
import threading
import time
import traceback
import typing as ta


##


def dump_threads(out: ta.IO) -> None:
    out.write('\n\n')

    thrs_by_tid = {t.ident: t for t in threading.enumerate()}

    for tid, fr in sys._current_frames().items():  # noqa
        try:
            thr = thrs_by_tid[tid]
        except KeyError:
            thr_rpr = repr(tid)
        else:
            thr_rpr = repr(thr)

        tb = traceback.format_stack(fr)

        out.write(f'{thr_rpr}\n')
        out.write('\n'.join(l.strip() for l in tb))
        out.write('\n\n')


def dump_threads_str() -> str:
    out = io.StringIO()
    dump_threads(out)
    return out.getvalue()


##


class StoppableThread:
    def __init__(
            self,
            fn: ta.Callable[[], None],
            interval_s: float,
            *,
            tick_immediately: bool = False,
            start: bool = False,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__()
        self._fn = fn
        self._interval_s = interval_s
        self._tick_immediately = tick_immediately
        self._thread = threading.Thread(target=self._loop, **kwargs)
        self._stop_event = threading.Event()
        if start:
            self.start()

    @property
    def thread(self) -> threading.Thread:
        return self._thread

    @property
    def ident(self) -> int | None:
        return self._thread.ident

    def start(self) -> None:
        return self._thread.start()

    def stop_nowait(self) -> None:
        self._stop_event.set()

    def stop_wait(self, timeout: float | None = None) -> None:
        self.stop_nowait()
        self._thread.join(timeout)

    def _loop(self) -> None:
        if self._tick_immediately:
            self._fn()

        while True:
            self._stop_event.wait(self._interval_s)
            if self._stop_event.is_set():
                return

            self._fn()


##


_DEBUG_THREAD_COUNTER = itertools.count()


def create_thread_dump_thread(
        *,
        interval_s: float = 5.,
        out: ta.TextIO = sys.stderr,
        start: bool = False,
        nodaemon: bool = False,
) -> StoppableThread:
    def proc() -> None:
        try:
            out.write(dump_threads_str())
        except Exception as e:  # noqa
            out.write(repr(e) + '\n\n')

    return StoppableThread(
        proc,
        interval_s,
        daemon=not nodaemon,
        name=f'thread-dump-thread-{next(_DEBUG_THREAD_COUNTER)}',
        start=start,
    )


##


def create_suicide_thread(
        *,
        sig: int = signal.SIGKILL,
        interval_s: float = 1.,
        parent_thread: threading.Thread | None = None,
        start: bool = False,
) -> StoppableThread:
    """Kills process when parent_thread dies."""

    if parent_thread is None:
        parent_thread = threading.current_thread()

    def proc() -> None:
        if not parent_thread.is_alive():
            os.kill(os.getpid(), sig)

    return StoppableThread(
        proc,
        interval_s,
        name=f'suicide-thread-{next(_DEBUG_THREAD_COUNTER)}',
        start=start,
    )


##


def create_timebomb_thread(
        delay_s: float,
        *,
        sig: int = signal.SIGKILL,
        interval_s: float = 1.,
        start: bool = False,
) -> StoppableThread:
    def proc() -> None:
        if time.time() >= deadline:
            os.kill(os.getpid(), sig)

    deadline = time.time() + delay_s

    return StoppableThread(
        proc,
        interval_s,
        name=f'timebomb-thread-{next(_DEBUG_THREAD_COUNTER)}',
        start=start,
    )
