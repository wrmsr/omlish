# ruff: noqa: UP007
import logging
import os
import typing as ta


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
        return existing_dirpath(val)


##


def octal_type(arg: ta.Union[str, int]) -> int:
    if isinstance(arg, int):
        return arg
    try:
        return int(arg, 8)
    except (TypeError, ValueError):
        raise ValueError(f'{arg} can not be converted to an octal type')  # noqa


def existing_directory(v: str) -> str:
    nv = os.path.expanduser(v)
    if os.path.isdir(nv):
        return nv
    raise ValueError(f'{v} is not an existing directory')


def existing_dirpath(v: str) -> str:
    nv = os.path.expanduser(v)
    dir = os.path.dirname(nv)  # noqa
    if not dir:
        # relative pathname with no directory component
        return nv
    if os.path.isdir(dir):
        return nv
    raise ValueError(f'The directory named as part of the path {v} does not exist')


def logging_level(value: ta.Union[str, int]) -> int:
    if isinstance(value, int):
        return value
    s = str(value).lower()
    level = logging.getLevelNamesMapping().get(s.upper())
    if level is None:
        raise ValueError(f'bad logging level name {value!r}')
    return level


class SuffixMultiplier:
    # d is a dictionary of suffixes to integer multipliers.  If no suffixes match, default is the multiplier.  Matches
    # are case insensitive.  Return values are in the fundamental unit.
    def __init__(self, d, default=1):
        super().__init__()
        self._d = d
        self._default = default
        # all keys must be the same size
        self._keysz = None
        for k in d:
            if self._keysz is None:
                self._keysz = len(k)
            elif self._keysz != len(k):  # type: ignore
                raise ValueError(k)

    def __call__(self, v: ta.Union[str, int]) -> int:
        if isinstance(v, int):
            return v
        v = v.lower()
        for s, m in self._d.items():
            if v[-self._keysz:] == s:  # type: ignore
                return int(v[:-self._keysz]) * m  # type: ignore
        return int(v) * self._default


byte_size = SuffixMultiplier({
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
})


class RestartWhenExitUnexpected:
    pass


class RestartUnconditionally:
    pass
