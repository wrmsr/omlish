try:
    from billiard import *  # noqa
    from billiard import process  # noqa
    from billiard import queues  # noqa

except ImportError:
    from multiprocessing import *  # noqa
    from multiprocessing import process  # noqa
    from multiprocessing import queues  # noqa


import concurrent.futures as cf
import contextlib
import functools
import typing as ta


class _PendingWorkItems:

    def __init__(self, dct, fn):
        super().__init__()

        if not isinstance(dct, dict):
            raise TypeError(dct)
        if not callable(fn):
            raise TypeError(fn)

        self._dct = dct
        self._fn = fn

    def pop(self, k, default=None):
        return self._dct.pop(k, default)

    def items(self):
        return self._dct.items()

    def clear(self):
        return self._dct.clear()

    def __bool__(self):
        return bool(self._dct)

    def __getitem__(self, k):
        return self._dct[k]

    def __setitem__(self, k, v):
        if not isinstance(v, cf.process._WorkItem):  # noqa
            raise TypeError(v)
        fn = v.fn
        args = list(v.args or [])
        kwargs = dict(v.kwargs or {})
        if isinstance(fn, functools.partial):
            args = [*fn.args, *args]
            kwargs = {**fn.keywords, **kwargs}
            fn = fn.func
        if fn is not self._fn:
            raise ValueError(fn)
        self._dct[k] = cf.process._WorkItem(v.future, None, args, kwargs)  # noqa

    def __delitem__(self, k):
        del self._dct[k]


@contextlib.contextmanager
def forking_process_pool(fn: ta.Callable, *args, **kwargs) -> ta.Iterator[cf.Executor]:
    """
    Workaround for https://bugs.python.org/issue33725 to force forking (enabling CoW of non-picklable state). Per ticket
    can't be safely used in a process touching obj-c runtime internals. Caller beware.
    """

    if not callable(fn):
        raise TypeError(fn)

    if 'mp_context' not in kwargs:
        kwargs['mp_context'] = get_context('fork')  # noqa

    exe: ta.Any
    with cf.ProcessPoolExecutor(*args, **kwargs) as exe:
        pwi = _PendingWorkItems(exe._pending_work_items, fn)  # noqa
        exe._pending_work_items = pwi
        exe._call_queue.pending_work_items = pwi  # noqa

        for o in [exe, exe._call_queue]:
            for a, v in o.__dict__.items():
                if v is pwi._dct:
                    raise ValueError(v)

        def call_queue_get(block=True, timeout=None):
            v = orig_call_queue_get(block, timeout)
            if v is not None:
                if not isinstance(v, cf.process._CallItem):  # noqa
                    raise TypeError(v)
                v = cf.process._CallItem(v.work_id, fn, v.args, v.kwargs)  # noqa
            return v

        orig_call_queue_get = exe._call_queue.get  # noqa
        exe._call_queue.get = call_queue_get  # noqa

        yield ta.cast(cf.ProcessPoolExecutor, exe)
