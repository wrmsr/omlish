# @omlish-lite
import logging
import typing as ta

from .protocols import LoggerLike


##


def get_module_logger(mod_globals: ta.Mapping[str, ta.Any]) -> LoggerLike:
    return logging.getLogger(mod_globals.get('__name__'))  # noqa
