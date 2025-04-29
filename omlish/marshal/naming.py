"""
TODO:
 - Namer: ta.TypeAlias = ta.Callable[[str], str] ?
  - this interface is ~intentionally~ limited, but custom overrides would be useful
"""
import enum

from .. import lang
from .base import Option


class Naming(Option, enum.Enum):
    SNAKE = 'snake'
    CAMEL = 'camel'
    LOW_CAMEL = 'low_camel'


def translate_name(n: str, e: Naming) -> str:
    if e is Naming.SNAKE:
        return lang.snake_case(*lang.split_string_casing(n))
    if e is Naming.CAMEL:
        return lang.camel_case(*lang.split_string_casing(n))
    if e is Naming.LOW_CAMEL:
        return lang.low_camel_case(*lang.split_string_casing(n))
    raise ValueError(e)
