"""distutils.dist

Provides the Distribution class, which represents the module distribution
being built/installed/distributed.
"""

import contextlib
import logging
import os
import pathlib
import re
import sys
from collections.abc import Iterable
from email import message_from_file

try:
    import warnings
except ImportError:
    warnings = None

from ._log import log
from .debug import DEBUG
from .errors import (
    DistutilsArgError,
    DistutilsClassError,
    DistutilsModuleError,
    DistutilsOptionError,
)
from .util import check_environ, rfc822_escape, strtobool

# Regex to define acceptable Distutils command names.  This is not *quite*
# the same as a Python NAME -- I don't allow leading underscores.  The fact
# that they're very similar is no coincidence; the default naming scheme is
# to look for a Python module named after the command.
command_re = re.compile(r'^[a-zA-Z]([a-zA-Z0-9_]*)$')


def _ensure_list(value, fieldname):
    if isinstance(value, str):
        # a string containing comma separated values is okay.  It will
        # be converted to a list by Distribution.finalize_options().
        pass
    elif not isinstance(value, list):
        # passing a tuple or an iterator perhaps, warn and convert
        typename = type(value).__name__
        msg = "Warning: '{fieldname}' should be a list, got type '{typename}'"
        msg = msg.format(**locals())
        log.warning(msg)
        value = list(value)
    return value


