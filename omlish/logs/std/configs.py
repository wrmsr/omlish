# ruff: noqa: UP006 UP045
# @omlish-lite
"""
https://docs.python.org/3/howto/logging.html#configuring-logging
https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
"""
import dataclasses as dc
import typing as ta


FilterDictLoggingConfig = ta.Dict[str, ta.Any]  # ta.TypeAlias
FormatterDictLoggingConfig = ta.Dict[str, ta.Any]  # ta.TypeAlias
HandlerDictLoggingConfig = ta.Dict[str, ta.Any]  # ta.TypeAlias
LoggerDictLoggingConfig = ta.Dict[str, ta.Any]  # ta.TypeAlias


##


@dc.dataclass()
class DictLoggingConfig:
    version: int = 1
    incremental: bool = False
    disable_existing_loggers: bool = False
    filters: ta.Dict[str, FilterDictLoggingConfig] = dc.field(default_factory=dict)
    formatters: ta.Dict[str, FormatterDictLoggingConfig] = dc.field(default_factory=dict)
    handlers: ta.Dict[str, HandlerDictLoggingConfig] = dc.field(default_factory=dict)
    loggers: ta.Dict[str, LoggerDictLoggingConfig] = dc.field(default_factory=dict)
    root: ta.Optional[LoggerDictLoggingConfig] = None
