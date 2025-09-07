# @omlish-lite
import logging
import typing as ta

from .base import Logger
from .std.loggers import StdLogger


##


def get_module_logger(mod_globals: ta.Mapping[str, ta.Any]) -> Logger:
    return StdLogger(logging.getLogger(mod_globals.get('__name__')))  # noqa
