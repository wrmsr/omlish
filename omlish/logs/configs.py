"""
https://docs.python.org/3/howto/logging.html#configuring-logging
"""
import dataclasses as dc
import typing as ta


##


FilterConfig: ta.TypeAlias = dict[str, ta.Any]
FormatterConfig: ta.TypeAlias = dict[str, ta.Any]
HandlerConfig: ta.TypeAlias = dict[str, ta.Any]
LoggerConfig: ta.TypeAlias = dict[str, ta.Any]


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
