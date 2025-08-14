"""
TODO:
 - quantiles via math.histogram
"""
import atexit
import contextlib
import functools
import sys
import threading
import time
import typing as ta

from .. import check
from .. import lang


T = ta.TypeVar('T')


##


class _GlobalTimer:
    def __init__(
            self,
            registry: '_GlobalTimerRegistry',
            name: str,
            *,
            clock: ta.Callable[[], float] | None = None,
            report_at_exit: bool = False,
            report_out: ta.Any | None = None,
    ) -> None:
        super().__init__()

        self._registry = registry
        self._name = name

        if clock is None:
            clock = time.monotonic
        self._clock = clock
        self._report_out = report_out

        self._lock = threading.Lock()

        self._c = 0
        self._t = 0.

        if report_at_exit:
            atexit.register(self.report)

    def report(self) -> None:
        msg = (
            f'{self._registry.module_name}::{self._name}: '
            f'{self._c} calls, '
            f'{self._t:.3f}s total'
        )

        print(
            msg,
            file=self._report_out if self._report_out is not None else sys.stderr,
        )

    @contextlib.contextmanager
    def __call__(self) -> ta.Iterator[None]:
        start = self._clock()

        try:
            yield

        finally:
            end = self._clock()
            took = end - start

            with self._lock:
                self._c += 1
                self._t += took


#


class _GlobalTimerRegistry:
    def __init__(
            self,
            module_name: str,
    ) -> None:
        super().__init__()

        self._module_name = module_name

        self._lock = threading.Lock()

        self._timers: dict[str, _GlobalTimer] = {}

    @property
    def module_name(self) -> str:
        return self._module_name

    def get_timer(
            self,
            name: str,
            **kwargs: ta.Any,
    ) -> _GlobalTimer:
        return lang.double_check_setdefault(
            self._lock,
            self._timers,
            name,
            lambda: _GlobalTimer(
                self,
                name,
                **kwargs,
            ),
        )


_GLOBAL_LOCK = threading.Lock()
_GLOBAL_ATTR = '__global_timers_registry__'


def _get_global_registry(
        globals: ta.MutableMapping[str, ta.Any],  # noqa
) -> _GlobalTimerRegistry:
    reg = lang.double_check_setdefault(
        _GLOBAL_LOCK,
        globals,
        _GLOBAL_ATTR,
        lambda: _GlobalTimerRegistry(
            globals['__name__'],
        ),
    )

    return check.isinstance(reg, _GlobalTimerRegistry)


#


@contextlib.contextmanager
def global_timer_context(
        globals: ta.MutableMapping[str, ta.Any],  # noqa
        name: str,
        **kwargs: ta.Any,
) -> ta.Iterator[None]:
    reg = _get_global_registry(globals)
    timer = reg.get_timer(name, **kwargs)
    with timer():
        yield


#


class _GlobalTimerContextWrapped:
    def __init__(
            self,
            fn: ta.Any,
            timer: _GlobalTimer,
    ) -> None:
        super().__init__()

        self._fn = fn
        self._timer = timer

        functools.update_wrapper(self, fn)

    def __get__(self, instance, owner=None):
        return self.__class__(
            self._fn.__get__(instance, owner),
            self._timer,
        )

    def __call__(self, *args, **kwargs):
        with self._timer():
            return self._fn(*args, **kwargs)


def global_timer_wrap(
        globals: ta.MutableMapping[str, ta.Any],  # noqa
        name: str,
        **kwargs: ta.Any,
) -> ta.Callable[[T], T]:
    reg = _get_global_registry(globals)
    timer = reg.get_timer(name, **kwargs)

    def inner(fn):
        return _GlobalTimerContextWrapped(fn, timer)

    return inner
