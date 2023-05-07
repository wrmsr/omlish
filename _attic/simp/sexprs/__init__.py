"""
TODO:
 - usecase:
  - when don't have AST access (omni core)
  - when want a non-reprable const but but dont want to do ast construction
  - as shorthand when transforming

['def', 'f', ['x', 'y']
 ['return' ['+', 'x', 'y']]]

['def', 'say_hello', []
 ['print', c('hi')]]

['def', 'sum_pt', ['pt'],
 ['return', ['+', 'pt.x', 'pt.y']]]
"""
from . import macros  # noqa
from .macros import DEFAULT_MACROS  # noqa
from .macros import dynamic_macro  # noqa
from .macros import DynamicMacro  # noqa
from .macros import named_macro  # noqa
from .macros import NamedMacro  # noqa
from .types import Args  # noqa
from .types import Macro  # noqa
from .types import Matcher  # noqa
from .types import Xlat  # noqa
from .xlat import c  # noqa
from .xlat import xlat  # noqa
from .xlat import Xlator  # noqa
