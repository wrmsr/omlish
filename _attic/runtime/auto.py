from .current import get
from .facets.errors import Errors
from .facets.logging import Logger
from .facets.metrics import Metrics


class _AutoDescriptor:
    def __init__(self):
        super().__init__()
        self._name = None

    def __set_name__(self, owner, name):
        if name and self._name is None:
            self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(getattr(instance, '_underlying'), self._name)


class AutoErrors(Errors):
    @property
    def _underlying(self) -> Errors:
        return get().errors

    report = _AutoDescriptor()


errors: Errors = AutoErrors()


class AutoLogger(Logger):
    @property
    def _underlying(self) -> Logger:
        return get().log

    wrapped = _AutoDescriptor()
    debug = _AutoDescriptor()
    info = _AutoDescriptor()
    warning = _AutoDescriptor()
    error = _AutoDescriptor()
    exception = _AutoDescriptor()
    critical = _AutoDescriptor()
    log = _AutoDescriptor()
    is_enabled_for = _AutoDescriptor()
    get_effective_level = _AutoDescriptor()
    _log = _AutoDescriptor()


log: Logger = AutoLogger()


class AutoMetrics(Metrics):
    @property
    def _underlying(self) -> Metrics:
        return get().metrics

    send = _AutoDescriptor()


metrics: Metrics = AutoMetrics()
