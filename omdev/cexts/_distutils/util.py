"""Miscellaneous utility functions -- anything that doesn't fit into one of the other *util.py modules."""
import functools
import os
import re
import string
import sys
import sysconfig
import typing as ta

from omlish.logs import all as logs

from .errors import DistutilsPlatformError


log = logs.get_module_logger(globals())


##


def pass_none(func):
    """Wrap func so it's not called if its first param is None"""

    @functools.wraps(func)
    def wrapper(param, *args, **kwargs):
        if param is not None:
            return func(param, *args, **kwargs)
        return None

    return wrapper


def always_iterable(obj, base_type=(str, bytes)):
    if obj is None:
        return iter(())

    if (base_type is not None) and isinstance(obj, base_type):
        return iter((obj,))

    try:
        return iter(obj)
    except TypeError:
        return iter((obj,))


def get_host_platform() -> str:
    """
    Return a string that identifies the current platform. Use this function to distinguish platform-specific build
    directories and platform-specific built distributions.
    """

    # This function initially exposed platforms as defined in Python 3.9 even with older Python versions when distutils
    # was split out. Now it delegates to stdlib sysconfig, but maintains compatibility.

    return sysconfig.get_platform()


_syscfg_macosx_ver: ta.Any

if sys.platform == 'darwin':
    _syscfg_macosx_ver = None  # cache the version pulled from sysconfig


def _clear_cached_macosx_ver() -> None:
    """For testing only. Do not call."""
    global _syscfg_macosx_ver
    _syscfg_macosx_ver = None


MACOSX_VERSION_VAR = 'MACOSX_DEPLOYMENT_TARGET'


def get_macosx_target_ver_from_syscfg() -> str:
    """
    Get the version of macOS latched in the Python interpreter configuration. Returns the version as a string or None
    if can't obtain one. Cached.
    """
    global _syscfg_macosx_ver
    if _syscfg_macosx_ver is None:
        from . import sysconfig

        ver = sysconfig.get_config_var(MACOSX_VERSION_VAR) or ''
        if ver:
            _syscfg_macosx_ver = ver
    return _syscfg_macosx_ver


def get_macosx_target_ver() -> str:
    """
    Return the version of macOS for which we are building.

    The target version defaults to the version in sysconfig latched at time the Python interpreter was built, unless
    overridden by an environment variable. If neither source has a value, then None is returned
    """

    syscfg_ver = get_macosx_target_ver_from_syscfg()
    env_ver = os.environ.get(MACOSX_VERSION_VAR)

    if env_ver:
        # Validate overridden version against sysconfig version, if have both. Ensure that the deployment target of the
        # build process is not less than 10.3 if the interpreter was built for 10.3 or later.  This ensures extension
        # modules are built with correct compatibility values, specifically LDSHARED which can use '-undefined
        # dynamic_lookup' which only works on >= 10.3.
        if (
                syscfg_ver
                and split_version(syscfg_ver) >= [10, 3] > split_version(env_ver)
        ):
            my_msg = ''.join([
                '$',
                MACOSX_VERSION_VAR,
                ' mismatch: ',
                f'now "{env_ver}" but "{syscfg_ver}" during configure; ',
                'must use 10.3 or later',
            ])
            raise DistutilsPlatformError(my_msg)
        return env_ver
    return syscfg_ver


def split_version(s) -> list[int]:
    """Convert a dot-separated string into a list of numbers for comparisons"""
    return [int(n) for n in s.split('.')]


_wordchars_re = re.compile(r'[^\\\'\"%s ]*' % string.whitespace)  # noqa
_squote_re = re.compile(r"'(?:[^'\\]|\\.)*'")
_dquote_re = re.compile(r'"(?:[^"\\]|\\.)*"')


def split_quoted(s: str) -> list[str]:
    """
    Split a string up according to Unix shell-like rules for quotes and backslashes.  In short: words are delimited by
    spaces, as long as those spaces are not escaped by a backslash, or inside a quoted string. Single and double quotes
    are equivalent, and the quote characters can be backslash-escaped.  The backslash is stripped from any two-character
    escape sequence, leaving only the escaped character.  The quote characters are stripped from any quoted string.
    Returns a list of words.
    """

    s = s.strip()
    words = []
    pos = 0

    while s:
        m = _wordchars_re.match(s, pos)
        if m is None:
            raise ValueError(s)
        end = m.end()
        if end == len(s):
            words.append(s[:end])
            break

        if s[end] in string.whitespace:
            # unescaped, unquoted whitespace: now we definitely have a word delimiter
            words.append(s[:end])
            s = s[end:].lstrip()
            pos = 0

        elif s[end] == '\\':
            # preserve whatever is being escaped; will become part of the current word
            s = s[:end] + s[end + 1:]
            pos = end + 1

        else:
            if s[end] == "'":  # slurp singly-quoted string
                m = _squote_re.match(s, end)
            elif s[end] == '"':  # slurp doubly-quoted string
                m = _dquote_re.match(s, end)
            else:
                raise RuntimeError(f"this can't happen (bad char '{s[end]}')")

            if m is None:
                raise ValueError(f'bad string (mismatched {s[end]} quotes?)')

            (beg, end) = m.span()
            s = s[:beg] + s[beg + 1: end - 1] + s[end:]
            pos = m.end() - 2

        if pos >= len(s):
            words.append(s)
            break

    return words


def execute(
        func: ta.Callable,
        args: ta.Iterable,
        msg: str | None = None,
        verbose: int = 0,
        dry_run: bool = False,
) -> None:
    """
    Perform some action that affects the outside world (eg.  by writing to the filesystem).  Such actions are special
    because they are disabled by the 'dry_run' flag.  This method takes care of all that bureaucracy for you; all you
    have to do is supply the function to call and an argument tuple for it (to embody the "external action" being
    performed), and an optional message to print.
    """
    if msg is None:
        msg = f'{func.__name__}{args!r}'
        if msg[-2:] == ',)':  # correct for singleton tuple
            msg = msg[0:-2] + ')'

    log.info(msg)
    if not dry_run:
        func(*args)
