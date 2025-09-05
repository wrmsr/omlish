# @omlish-lite
import logging
import typing as ta


##


def get_module_logger(mod_globals: ta.Mapping[str, ta.Any]) -> logging.Logger:
    return logging.getLogger(mod_globals.get('__name__'))
