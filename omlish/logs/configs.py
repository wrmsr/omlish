import dataclasses as dc
import logging
import typing as ta

from ..lite.logs import configure_standard_logging as configure_lite_standard_logging


##


NOISY_LOGGERS: set[str] = {
    'boto3.resources.action',
    'datadog.dogstatsd',
    'elasticsearch',
    'kazoo.client',
    'requests.packages.urllib3.connectionpool',
}


##


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


##


def configure_standard_logging(
        level: ta.Any = None,
        *,
        json: bool = False,
) -> logging.Handler:
    handler = configure_lite_standard_logging(
        level,
        json=json,
    )

    for noisy_logger in NOISY_LOGGERS:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    return handler
