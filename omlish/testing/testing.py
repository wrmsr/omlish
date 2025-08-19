# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import functools
import os
import sys
import threading
import time
import traceback
import typing as ta


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


def assert_dicts_equal_ordered(l: ta.Mapping[K, V], r: ta.Mapping[K, V]) -> None:
    assert list(l.items()) == list(r.items())


##


DEFAULT_TIMEOUT_S = 30


def call_many_with_timeout(
        fns: ta.Iterable[ta.Callable[[], T]],
        timeout_s: ta.Optional[float] = None,
        timeout_exception: Exception = TimeoutError('Thread timeout'),
) -> ta.List[T]:
    if timeout_s is None:
        timeout_s = DEFAULT_TIMEOUT_S

    fns = list(fns)
    missing = object()
    rets: ta.List[ta.Any] = [missing] * len(fns)
    thread_exception: ta.Optional[Exception] = None

    def inner(fn, idx):
        try:
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

    return ta.cast('ta.List[T]', rets)


def run_with_timeout(
        *fns: ta.Callable[[], None],
        timeout_s: ta.Optional[float] = None,
        timeout_exception: Exception = TimeoutError('Thread timeout'),
) -> None:
    call_many_with_timeout(fns, timeout_s, timeout_exception)


def waitpid_with_timeout(
        pid: int,
        timeout_s: ta.Optional[float] = None,
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


##


def xfail(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception:  # noqa
            traceback.print_exc()

    return inner


def raise_in_thread(thr: threading.Thread, exc: ta.Union[BaseException, ta.Type[BaseException]]) -> None:
    if sys.implementation.name != 'cpython':
        raise RuntimeError(sys.implementation.name)

    # https://github.com/python/cpython/blob/37ba7531a59a0a2b240a86f7e2adfb1b1cd8ac0c/Lib/test/test_threading.py#L182
    import ctypes as ct
    ct.pythonapi.PyThreadState_SetAsyncExc(ct.c_ulong(thr.ident), ct.py_object(exc))  # type: ignore


##


def run_all_tests(
        obj: ta.Any,
        *,
        filter: ta.Optional[ta.Callable[[str, ta.Any], bool]] = None,  # noqa
        out: ta.Optional[ta.Any] = None,
) -> None:
    if out is None:
        out = sys.stderr

    if isinstance(obj, ta.Mapping):
        items: ta.Any = obj.items()
    else:
        items = ((a, getattr(obj, a)) for a in dir(obj))

    for k, v in items:
        if not callable(v):
            continue

        if filter is not None:
            if not filter(k, v):
                continue
        elif not k.startswith('test_'):
            continue

        print(f'Running {k}', file=out)
