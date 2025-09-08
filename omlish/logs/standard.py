# ruff: noqa: N802 UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - !! move to std !!
 - structured
 - prefixed
 - debug
 - optional noisy? noisy will never be lite - some kinda configure_standard callback mechanism?
"""
import contextlib
import datetime
import logging
import typing as ta

from .std.filters import TidLoggingFilter
from .std.json import JsonLoggingFormatter
from .std.proxy import ProxyLoggingHandler


##


STANDARD_LOG_FORMAT_PARTS = [
    ('asctime', '%(asctime)-15s'),
    ('process', 'pid=%(process)s'),
    ('thread', 'tid=%(thread)x'),
    ('levelname', '%(levelname)s'),
    ('name', '%(name)s'),
    ('separator', '::'),
    ('message', '%(message)s'),
]


class StandardLoggingFormatter(logging.Formatter):
    @staticmethod
    def build_log_format(parts: ta.Iterable[ta.Tuple[str, str]]) -> str:
        return ' '.join(v for k, v in parts)

    converter = datetime.datetime.fromtimestamp  # type: ignore

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            return ct.strftime(datefmt)  # noqa
        else:
            t = ct.strftime('%Y-%m-%d %H:%M:%S')
            return '%s.%03d' % (t, record.msecs)  # noqa


##


class StandardConfiguredLoggingHandler(ProxyLoggingHandler):
    def __init_subclass__(cls, **kwargs):
        raise TypeError('This class serves only as a marker and should not be subclassed.')


##


@contextlib.contextmanager
def _locking_logging_module_lock() -> ta.Iterator[None]:
    if hasattr(logging, '_acquireLock'):
        logging._acquireLock()  # noqa
        try:
            yield
        finally:
            logging._releaseLock()  # type: ignore  # noqa

    elif hasattr(logging, '_lock'):
        # https://github.com/python/cpython/commit/74723e11109a320e628898817ab449b3dad9ee96
        with logging._lock:  # noqa
            yield

    else:
        raise Exception("Can't find lock in logging module")


def configure_standard_logging(
        level: ta.Union[int, str] = logging.INFO,
        *,
        target: ta.Optional[logging.Logger] = None,

        force: bool = False,

        handler_factory: ta.Optional[ta.Callable[[], logging.Handler]] = None,

        formatter: ta.Optional[logging.Formatter] = None,  # noqa
        json: bool = False,
) -> ta.Optional[StandardConfiguredLoggingHandler]:
    with _locking_logging_module_lock():
        if target is None:
            target = logging.root

        #

        if not force:
            if any(isinstance(h, StandardConfiguredLoggingHandler) for h in list(target.handlers)):
                return None

        #

        if handler_factory is not None:
            handler = handler_factory()
        else:
            handler = logging.StreamHandler()

        #

        if formatter is None:
            if json:
                formatter = JsonLoggingFormatter()
            else:
                formatter = StandardLoggingFormatter(StandardLoggingFormatter.build_log_format(STANDARD_LOG_FORMAT_PARTS))  # noqa
        handler.setFormatter(formatter)

        #

        handler.addFilter(TidLoggingFilter())

        #

        target.addHandler(handler)

        #

        if level is not None:
            target.setLevel(level)

        #

        return StandardConfiguredLoggingHandler(handler)
