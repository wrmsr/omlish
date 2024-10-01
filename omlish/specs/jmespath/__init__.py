"""
TODO:
 - @omlish-lite
"""
from . import exceptions  # noqa
from . import functions  # noqa
from . import lexer  # noqa
from . import parser  # noqa

from .parser import (  # noqa
    compile,
    search,
)

from .visitor import (  # noqa
    Options,
)


__version__ = '1.0.1'
