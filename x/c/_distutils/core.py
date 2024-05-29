"""distutils.core

The only module that needs to be imported to use the Distutils; provides
the 'setup' function (which is to be called from the setup script).  Also
indirectly provides the Distribution and Command classes, although they are
really defined in distutils.dist and distutils.cmd.
"""

import os
import sys
import tokenize

from .debug import DEBUG

# Mainly import these so setup scripts can "from distutils.core import" them.
from .errors import (
    CCompilerError,
    DistutilsArgError,
    DistutilsError,
    DistutilsSetupError,
)
from .extension import Extension

__all__ = ['Extension']