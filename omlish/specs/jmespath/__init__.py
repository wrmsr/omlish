"""
TODO:
 - @omlish-lite

Applied:
 https://github.com/jmespath-community/python-jmespath/compare/bbe7300c60056f52413603cf3e2bcd0b6afeda3d...aef45e9d665de662eee31b06aeb8261e2bc8b90a

From community:
 - JEP-11 Lexical Scoping - https://github.com/jmespath-community/jmespath.spec/discussions/24#discussioncomment-3285710
 - JEP-11a Lexical Scoping deprecates the let function.
 - JEP-13 Object Manipulation functions - https://github.com/jmespath-community/jmespath.spec/discussions/47#discussioncomment-3308897
 - JEP-14 String functions - https://github.com/jmespath-community/jmespath.spec/discussions/21#discussioncomment-3869583
 - JEP-15 String Slices - https://github.com/jmespath-community/jmespath.spec/discussions/26#discussioncomment-3284127
 - JEP-16 Arithmetic Expressions - https://github.com/jmespath-community/jmespath.spec/discussions/25#discussioncomment-3277652
 - JEP-17 Root Reference - https://github.com/jmespath-community/jmespath.spec/discussions/18#discussion-3913993
 - JEP-18 Grouping - https://github.com/jmespath-community/jmespath.spec/discussions/96#discussion-4282156
 - JEP-19 Evaluation of Pipe Expressions - https://github.com/jmespath-community/jmespath.spec/discussions/113#discussioncomment-4000862
 - JEP-20 Compact syntax for multi-select-hash - https://github.com/jmespath-community/jmespath.spec/discussions/19

See:
 - https://github.com/jmespath-community/jmespath.spec/tree/main
 - https://github.com/jmespath-community/python-jmespath
 - https://github.com/jmespath-community/jmespath.spec/discussions?discussions_q=label%3Ajep-candidate
 - https://github.com/jmespath-community/jmespath.spec/discussions/97
"""  # noqa
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
