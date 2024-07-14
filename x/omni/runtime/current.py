import contextlib
import threading
import typing as ta

from .default import _DEFAULT
from .facets.errors import Errors
from .facets.logging import Logger
from .facets.metrics import Metrics
from .runtime import InvalidatableRuntime
from .runtime import Runtime


get: ta.Callable[..., Runtime]


class CurrentRuntime(Runtime):

    def errors(self) -> Errors:
        return get().errors

    def log(self) -> Logger:
        return get().log

    def metrics(self) -> Metrics:
        return get().metrics


_CURRENT = threading.local()


def get(default: ta.Optional[Runtime] = None) -> Runtime:
    try:
        rt = _CURRENT.runtime
    except AttributeError:
        if default is not None:
            rt = default
        else:
            rt = _DEFAULT
    if not isinstance(rt, Runtime):
        raise TypeError(rt)
    return rt


@contextlib.contextmanager
def setting_current(runtime: Runtime) -> Runtime:
    if not isinstance(runtime, Runtime):
        raise TypeError(runtime)
    ir = InvalidatableRuntime(runtime)
    try:
        prev = _CURRENT.runtime
    except AttributeError:
        prev = _DEFAULT
        reset = None
    else:
        reset = prev
    try:
        _CURRENT.runtime = ir
        yield prev
    finally:
        if reset is not None:
            _CURRENT.runtime = reset
        else:
            del _CURRENT.runtime
        ir.invalidate()
