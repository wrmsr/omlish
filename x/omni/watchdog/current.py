import contextlib
import functools
import threading
import typing as ta

from .. import check
from .types import NopWatchdog
from .types import Watchdog


_THREAD_LOCAL = threading.local()
_THREAD_LOCAL_INSTANCE_ATTR = 'instance'


def current() -> Watchdog:
    return check.isinstance(getattr(_THREAD_LOCAL, _THREAD_LOCAL_INSTANCE_ATTR, NopWatchdog()), Watchdog)


@contextlib.contextmanager
def enter_current(instance: Watchdog) -> ta.Iterator[Watchdog]:
    check.isinstance(instance, Watchdog)
    check.state(not hasattr(_THREAD_LOCAL, _THREAD_LOCAL_INSTANCE_ATTR))
    try:
        _THREAD_LOCAL.instance = instance
        yield instance
    finally:
        del _THREAD_LOCAL.instance


def inherit_current(target: ta.Callable) -> ta.Callable:
    @functools.wraps(target)
    def inner(*args, **kwargs):
        with enter_current(instance):
            return target(*args, **kwargs)

    instance = current()
    return inner
