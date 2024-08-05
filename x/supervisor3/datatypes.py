import grp
import logging
import os
import pwd
import signal


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


def name_to_uid(name: str) -> int:
    """
    Find a user ID from a string containing a user name or ID. Raises ValueError if the string can't be resolved to a
    valid user ID on the system.
    """
    try:
        uid = int(name)
    except ValueError:
        try:
            pwdrec = pwd.getpwnam(name)
        except KeyError:
            raise ValueError('Invalid user name %s' % name)
        uid = pwdrec[2]
    else:
        try:
            pwd.getpwuid(uid)  # check if uid is valid
        except KeyError:
            raise ValueError('Invalid user id %s' % name)
    return uid


def name_to_gid(name: str) -> int:
    """
    Find a group ID from a string containing a group name or ID. Raises ValueError if the string can't be resolved to a
    valid group ID on the system.
    """
    try:
        gid = int(name)
    except ValueError:
        try:
            grprec = grp.getgrnam(name)
        except KeyError:
            raise ValueError('Invalid group name %s' % name)
        gid = grprec[2]
    else:
        try:
            grp.getgrgid(gid)  # check if gid is valid
        except KeyError:
            raise ValueError('Invalid group id %s' % name)
    return gid


def gid_for_uid(uid: int) -> int:
    pwrec = pwd.getpwuid(uid)
    return pwrec[3]


def octal_type(arg: str | int) -> int:
    if isinstance(arg, int):
        return arg
    try:
        return int(arg, 8)
    except (TypeError, ValueError):
        raise ValueError('%s can not be converted to an octal type' % arg)


def existing_directory(v: str) -> str:
    nv = os.path.expanduser(v)
    if os.path.isdir(nv):
        return nv
    raise ValueError('%s is not an existing directory' % v)


def existing_dirpath(v: str) -> str:
    nv = os.path.expanduser(v)
    dir = os.path.dirname(nv)
    if not dir:
        # relative pathname with no directory component
        return nv
    if os.path.isdir(dir):
        return nv
    raise ValueError('The directory named as part of the path %s does not exist' % v)


def logging_level(value: str | int) -> int:
    if isinstance(value, int):
        return value
    s = str(value).lower()
    level = logging.getLevelNamesMapping().get(s.upper())
    if level is None:
        raise ValueError('bad logging level name %r' % value)
    return level


class SuffixMultiplier:
    # d is a dictionary of suffixes to integer multipliers.  If no suffixes match, default is the multiplier.  Matches
    # are case insensitive.  Return values are in the fundamental unit.
    def __init__(self, d, default=1):
        self._d = d
        self._default = default
        # all keys must be the same size
        self._keysz = None
        for k in d.keys():
            if self._keysz is None:
                self._keysz = len(k)
            else:
                assert self._keysz == len(k)

    def __call__(self, v: str | int) -> int:
        if isinstance(v, int):
            return v
        v = v.lower()
        for s, m in self._d.items():
            if v[-self._keysz:] == s:
                return int(v[:-self._keysz]) * m
        return int(v) * self._default


byte_size = SuffixMultiplier({
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
})


# all valid signal numbers
SIGNUMS = [getattr(signal, k) for k in dir(signal) if k.startswith('SIG')]


def signal_number(value: int | str) -> int:
    try:
        num = int(value)
    except (ValueError, TypeError):
        name = value.strip().upper()
        if not name.startswith('SIG'):
            name = 'SIG' + name
        num = getattr(signal, name, None)
        if num is None:
            raise ValueError('value %r is not a valid signal name' % value)
    if num not in SIGNUMS:
        raise ValueError('value %r is not a valid signal number' % value)
    return num


class RestartWhenExitUnexpected:
    pass


class RestartUnconditionally:
    pass
