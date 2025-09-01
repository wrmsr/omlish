# ruff: noqa: UP006 UP045
# @omlish-lite
"""
https://docs.python.org/3/howto/logging.html#configuring-logging
https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
"""
import dataclasses as dc
import typing as ta


FilterConfig = ta.Dict[str, ta.Any]  # ta.TypeAlias
FormatterConfig = ta.Dict[str, ta.Any]  # ta.TypeAlias
HandlerConfig = ta.Dict[str, ta.Any]  # ta.TypeAlias
LoggerConfig = ta.Dict[str, ta.Any]  # ta.TypeAlias


##


@dc.dataclass()
class DictConfig:
    version: int = 1
    incremental: bool = False
    disable_existing_loggers: bool = False
    filters: ta.Dict[str, FilterConfig] = dc.field(default_factory=dict)
    formatters: ta.Dict[str, FormatterConfig] = dc.field(default_factory=dict)
    handlers: ta.Dict[str, HandlerConfig] = dc.field(default_factory=dict)
    loggers: ta.Dict[str, LoggerConfig] = dc.field(default_factory=dict)
    root: ta.Optional[LoggerConfig] = None
