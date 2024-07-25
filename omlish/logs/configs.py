import dataclasses as dc
import logging
import typing as ta

from .filters import TidFilter
from .formatters import StandardLogFormatter


NOISY_LOGGERS: set[str] = {
    'boto3.resources.action',
    'datadog.dogstatsd',
    'elasticsearch',
    'kazoo.client',
    'requests.packages.urllib3.connectionpool',
}


@dc.dataclass()
class DictConfig:
    version: int = 1
    incremental: bool = False
    disable_existing_loggers: bool = False
    filters: dict[str, 'FilterConfig'] = dc.field(default_factory=dict)
    formatters: dict[str, 'FormatterConfig'] = dc.field(default_factory=dict)
    handlers: dict[str, 'HandlerConfig'] = dc.field(default_factory=dict)
    loggers: dict[str, 'LoggerConfig'] = dc.field(default_factory=dict)
    root: ta.Optional['LoggerConfig'] = None


FilterConfig = dict[str, ta.Any]
FormatterConfig = dict[str, ta.Any]
HandlerConfig = dict[str, ta.Any]
LoggerConfig = dict[str, ta.Any]

STANDARD_LOG_FORMAT_PARTS = [
    ('asctime', '%(asctime)-15s'),
    ('process', 'pid=%(process)-6s'),
    ('thread', 'tid=%(thread)-16s'),
    ('levelname', '%(levelname)-8s'),
    ('name', '%(name)s'),
    ('separator', '::'),
    ('message', '%(message)s'),
]


def build_log_format(parts: ta.Iterable[tuple[str, str]]) -> str:
    return ' '.join(v for k, v in parts)


def configure_standard_logging(level: ta.Any = None) -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(StandardLogFormatter(build_log_format(STANDARD_LOG_FORMAT_PARTS)))
    handler.addFilter(TidFilter())
    logging.root.addHandler(handler)

    if level is not None:
        logging.root.setLevel(level)

    for noisy_logger in NOISY_LOGGERS:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    return handler
