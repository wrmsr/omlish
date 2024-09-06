import dataclasses as dc
import logging
import typing as ta

from ..lite.logs import configure_standard_logging as configure_lite_standard_logging
from .noisy import silence_noisy_loggers


##


FilterConfig = dict[str, ta.Any]
FormatterConfig = dict[str, ta.Any]
HandlerConfig = dict[str, ta.Any]
LoggerConfig = dict[str, ta.Any]


@dc.dataclass()
class DictConfig:
    version: int = 1
    incremental: bool = False
    disable_existing_loggers: bool = False
    filters: dict[str, FilterConfig] = dc.field(default_factory=dict)
    formatters: dict[str, FormatterConfig] = dc.field(default_factory=dict)
    handlers: dict[str, HandlerConfig] = dc.field(default_factory=dict)
    loggers: dict[str, LoggerConfig] = dc.field(default_factory=dict)
    root: LoggerConfig | None = None


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

    silence_noisy_loggers()

    return handler
