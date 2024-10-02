"""
TODO:
 - @omlish-lite

Applied:
 https://github.com/jmespath-community/python-jmespath/compare/bbe7300c60056f52413603cf3e2bcd0b6afeda3d...aef45e9d665de662eee31b06aeb8261e2bc8b90a

From community:
 - JEP-11 Lexical Scoping
 - JEP-11a Lexical Scoping deprecates the let function.
 - JEP-13 Object Manipulation functions
 - JEP-14 String functions
 - JEP-15 String Slices
 - JEP-16 Arithmetic Expressions
 - JEP-17 Root Reference
 - JEP-18 Grouping
 - JEP-19 Evaluation of Pipe Expressions
-
See:
 - https://github.com/jmespath-community/jmespath.spec/tree/main
 - https://github.com/jmespath-community/python-jmespath
 - https://github.com/jmespath-community/jmespath.spec/discussions?discussions_q=label%3Ajep-candidate
 - https://github.com/jmespath-community/jmespath.spec/discussions/97
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
