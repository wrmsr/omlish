import logging

from textual import LogGroup  # noqa
from textual import LogVerbosity  # noqa


##


def translate_log_level(level: int) -> tuple[LogGroup, LogVerbosity]:
    if level >= logging.ERROR:
        return (LogGroup.ERROR, LogVerbosity.HIGH)
    elif level >= logging.WARNING:
        return (LogGroup.ERROR, LogVerbosity.HIGH)
    elif level >= logging.INFO:
        return (LogGroup.INFO, LogVerbosity.NORMAL)
    elif level >= logging.DEBUG:
        return (LogGroup.DEBUG, LogVerbosity.NORMAL)
    else:
        return (LogGroup.UNDEFINED, LogVerbosity.NORMAL)
