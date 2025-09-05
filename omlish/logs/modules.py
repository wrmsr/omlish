# @omlish-lite
import logging
import typing as ta

from .protocols import LoggerLike
from .std.adapters import StdLogger


##


def get_module_logger(mod_globals: ta.Mapping[str, ta.Any]) -> LoggerLike:
    return StdLogger(logging.getLogger(mod_globals.get('__name__')))  # noqa
