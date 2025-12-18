# ruff: noqa: UP006
# @omlish-lite
import logging
import typing as ta

from .asyncs import LoggerToAsyncLogger
from .base import AsyncLogger
from .base import Logger
from .std.loggers import StdLogger


##


def _get_module_std_logger(mod_globals: ta.Mapping[str, ta.Any]) -> logging.Logger:
    return logging.getLogger(mod_globals.get('__name__'))


def get_module_logger(mod_globals: ta.Mapping[str, ta.Any]) -> Logger:
    return StdLogger(_get_module_std_logger(mod_globals))


def get_module_async_logger(mod_globals: ta.Mapping[str, ta.Any]) -> AsyncLogger:
    return LoggerToAsyncLogger(get_module_logger(mod_globals))


def get_module_loggers(mod_globals: ta.Mapping[str, ta.Any]) -> ta.Tuple[Logger, AsyncLogger]:
    return (
        log := get_module_logger(mod_globals),
        LoggerToAsyncLogger(log),
    )
