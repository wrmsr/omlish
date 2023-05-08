import io
import itertools
import os
import signal
import sys
import threading
import time
import traceback
import typing as ta


import pytest


_DEBUG_THREAD_COUNTER = itertools.count()


def create_thread_dump_thread(
        *,
        interval_s: ta.Union[int, float] = 5,
        out: ta.TextIO = sys.stderr,
        start: bool = False,
        nodaemon: bool = False,
) -> threading.Thread:
    def dump():
        cthr = threading.current_thread()
        thrs_by_tid = {t.ident: t for t in threading.enumerate()}

        buf = io.StringIO()
        for tid, fr in sys._current_frames().items():  # noqa
            if tid == cthr.ident:
                continue

            try:
                thr = thrs_by_tid[tid]
            except KeyError:
                thr_rpr = repr(tid)
            else:
                thr_rpr = repr(thr)

            tb = traceback.format_stack(fr)

            buf.write(f'{thr_rpr}\n')
            buf.write('\n'.join(l.strip() for l in tb))
            buf.write('\n\n')

        out.write(buf.getvalue())

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


def create_suicide_thread(
        *,
        sig: int = signal.SIGKILL,
        interval_s: ta.Union[int, float] = 1,
        parent_thread: ta.Optional[threading.Thread] = None,
        start: bool = False,
) -> threading.Thread:
    def proc():
        while True:
            parent_thread.join(interval_s)
            if not parent_thread.is_alive():
                os.kill(os.getpid(), sig)

    if parent_thread is None:
        parent_thread = threading.current_thread()

    dthr = threading.Thread(
        target=proc,
        name=f'suicide-thread-{next(_DEBUG_THREAD_COUNTER)}',
    )
    if start:
        dthr.start()
    return dthr


def raise_in_thread(thr: threading.Thread, exc: ta.Union[BaseException, ta.Type[BaseException]]) -> None:
    if sys.implementation.name != 'cpython':
        raise RuntimeError(sys.implementation.name)

    # https://github.com/python/cpython/blob/37ba7531a59a0a2b240a86f7e2adfb1b1cd8ac0c/Lib/test/test_threading.py#L182
    import ctypes as ct
    ct.pythonapi.PyThreadState_SetAsyncExc(ct.c_ulong(thr.ident), ct.py_object(exc))


###


@pytest.mark.skipif(sys.implementation.name != 'cpython', reason='cpython only')
def test_raise_in_thread():
    def proc():
        nonlocal c
        nonlocal f
        try:
            while True:
                time.sleep(.05)
                c += 1
        finally:
            f = True

    c = 0
    f = False
    t = threading.Thread(target=proc)
    t.start()
    assert t.is_alive()
    time.sleep(.4)
    assert not f
    raise_in_thread(t, SystemExit)
    t.join()
    assert not t.is_alive()
    assert c > 1
    assert f
