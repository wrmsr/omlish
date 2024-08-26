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


_DEBUG_THREAD_COUNTER = itertools.count()


def create_thread_dump_thread(
        *,
        interval_s: float = 5.,
        out: ta.TextIO = sys.stderr,
        start: bool = False,
        nodaemon: bool = False,
) -> threading.Thread:
    def dump():
        out.write(dump_threads())

    def proc():
        while True:
            time.sleep(interval_s)
            try:
                dump()
            except Exception as e:  # noqa
                out.write(repr(e) + '\n\n')

    dthr = threading.Thread(
        target=proc,
        daemon=not nodaemon,
        name=f'thread-dump-thread-{next(_DEBUG_THREAD_COUNTER)}',
    )
    if start:
        dthr.start()
    return dthr


##


def create_suicide_thread(
        *,
        sig: int = signal.SIGKILL,
        interval_s: float = 1.,
        parent_thread: threading.Thread | None = None,
        start: bool = False,
) -> threading.Thread:
    if parent_thread is None:
        parent_thread = threading.current_thread()

    def proc():
        while True:
            parent_thread.join(interval_s)
            if not parent_thread.is_alive():
                os.kill(os.getpid(), sig)

    dthr = threading.Thread(
        target=proc,
        name=f'suicide-thread-{next(_DEBUG_THREAD_COUNTER)}',
    )
    if start:
        dthr.start()
    return dthr
