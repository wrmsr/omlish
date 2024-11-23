# ruff: noqa: UP007
import logging
import typing as ta

from .utils.fs import check_path_with_existing_dir


class Automatic:
    pass


class Syslog:
    """TODO deprecated; remove this special 'syslog' filename in the future"""


LOGFILE_NONES = ('none', 'off', None)
LOGFILE_AUTOS = (Automatic, 'auto')
LOGFILE_SYSLOGS = (Syslog, 'syslog')


def logfile_name(val):
    if hasattr(val, 'lower'):
        coerced = val.lower()
    else:
        coerced = val

    if coerced in LOGFILE_NONES:
        return None
    elif coerced in LOGFILE_AUTOS:
        return Automatic
    elif coerced in LOGFILE_SYSLOGS:
        return Syslog
    else:
        return check_path_with_existing_dir(val)


##


def logging_level(value: ta.Union[str, int]) -> int:
    if isinstance(value, int):
        return value
    s = str(value).lower()
    level = logging.getLevelNamesMapping().get(s.upper())
    if level is None:
        raise ValueError(f'bad logging level name {value!r}')
    return level


class RestartWhenExitUnexpected:
    pass


class RestartUnconditionally:
    pass


class ExitNow(Exception):  # noqa
    pass
