"""
TODO:
 - Namer: ta.TypeAlias = ta.Callable[[str], str] ?
  - this interface is ~intentionally~ limited, but custom overrides would be useful
"""
import enum

from .. import check
from .. import lang
from .base.options import Option


##


class Naming(Option, enum.Enum):
    SNAKE = 'snake'
    CAMEL = 'camel'
    LOW_CAMEL = 'low_camel'


def translate_name(n: str, e: Naming) -> str:
    check.non_empty_str(n)
    check.not_equal(set(n), {'_'})

    n1 = n.lstrip('_')
    pfx = '_' * (len(n) - len(n1))
    n2 = n1.rstrip('_')
    sfx = '_' * (len(n1) - len(n2))
    ps = lang.split_string_casing(n2)

    if e is Naming.SNAKE:
        r = lang.snake_case(*ps)
    elif e is Naming.CAMEL:
        r = lang.camel_case(*ps)
    elif e is Naming.LOW_CAMEL:
        r = lang.low_camel_case(*ps)
    else:
        raise ValueError(e)

    return pfx + r + sfx
