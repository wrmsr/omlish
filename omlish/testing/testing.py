import functools
import importlib
import os
import sys
import threading
import time
import traceback
import typing as ta


DEFAULT_TIMEOUT_S = 30

T = ta.TypeVar('T')


def call_many_with_timeout(
        fns: ta.Iterable[ta.Callable[[], T]],
        timeout_s: float | None = None,
        timeout_exception: Exception = TimeoutError('Thread timeout'),
) -> list[T]:
    if timeout_s is None:
        timeout_s = DEFAULT_TIMEOUT_S

    fns = list(fns)
    missing = object()
    rets: list[ta.Any] = [missing] * len(fns)
    thread_exception: Exception | None = None

    def inner(fn, idx):
        try:
            nonlocal rets
            rets[idx] = fn()
        except Exception as e:
            nonlocal thread_exception
            thread_exception = e
            raise

    threads = [threading.Thread(target=inner, args=(fn, idx)) for idx, fn in enumerate(fns)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout_s)
    for thread in threads:
        if thread.is_alive():
            raise timeout_exception

    if thread_exception is not None:
        raise thread_exception
    for ret in rets:
        if ret is missing:
            raise ValueError

    return ta.cast(list[T], rets)


def run_with_timeout(
        *fns: ta.Callable[[], None],
        timeout_s: float | None = None,
        timeout_exception: Exception = TimeoutError('Thread timeout'),
) -> None:
    call_many_with_timeout(fns, timeout_s, timeout_exception)


def waitpid_with_timeout(
        pid: int,
        timeout_s: float | None = None,
        timeout_exception: Exception = TimeoutError('waitpid timeout'),
) -> int:
    if timeout_s is None:
        timeout_s = DEFAULT_TIMEOUT_S

    start_time = time.time()

    while True:
        wait_pid, status = os.waitpid(pid, os.WNOHANG)
        if wait_pid != 0:
            if wait_pid != pid:
                raise ValueError(f'{wait_pid} != {pid}')
            return status

        elapsed_time = time.time() - start_time
        if elapsed_time >= timeout_s:
            raise timeout_exception


def can_import(*args, **kwargs) -> bool:
    try:
        importlib.import_module(*args, **kwargs)
    except ImportError:
        return False
    else:
        return True


def xfail(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception:  # noqa
            traceback.print_exc()

    return inner


def raise_in_thread(thr: threading.Thread, exc: BaseException | type[BaseException]) -> None:
    if sys.implementation.name != 'cpython':
        raise RuntimeError(sys.implementation.name)

    # https://github.com/python/cpython/blob/37ba7531a59a0a2b240a86f7e2adfb1b1cd8ac0c/Lib/test/test_threading.py#L182
    import ctypes as ct
    ct.pythonapi.PyThreadState_SetAsyncExc(ct.c_ulong(thr.ident), ct.py_object(exc))  # type: ignore
