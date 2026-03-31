"""
TODO:
 - Namer: ta.TypeAlias = ta.Callable[[str], str] ?
  - this interface is ~intentionally~ limited, but custom overrides would be useful
"""
import enum
import typing as ta

from ... import check
from ... import lang
from .configs import Config


##


class Naming(Config, enum.Enum):
    CAMEL = 'camel'
    LOW_CAMEL = 'low_camel'
    SNAKE = 'snake'
    UP_SNAKE = 'up_snake'
    KEBAB = 'kebab'
    UP_KEBAB = 'up_kebab'


_CASING_BY_NAMING: ta.Mapping[Naming, lang.StringCasing] = {
    Naming.CAMEL: lang.CAMEL_CASE,
    Naming.LOW_CAMEL: lang.LOW_CAMEL_CASE,
    Naming.SNAKE: lang.SNAKE_CASE,
    Naming.UP_SNAKE: lang.UP_SNAKE_CASE,
    Naming.KEBAB: lang.KEBAB_CASE,
    Naming.UP_KEBAB: lang.UP_KEBAB_CASE,
}


def translate_name(n: str, e: Naming) -> str:
    check.non_empty_str(n)
    check.not_equal(set(n), {'_'})

    n1 = n.lstrip('_')
    pfx = '_' * (len(n) - len(n1))
    n2 = n1.rstrip('_')
    sfx = '_' * (len(n1) - len(n2))
    ps = lang.split_string_casing(n2)

    cs = _CASING_BY_NAMING[e]
    r = cs.join(*ps)

    return pfx + r + sfx
