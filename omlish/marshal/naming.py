import enum

from .. import lang
from .base import Option


class Naming(Option, enum.Enum):
    SNAKE = 'snake'
    CAMEL = 'camel'
    LOW_CAMEL = 'low_camel'


def translate_name(n: str, e: Naming) -> str:
    if e is Naming.SNAKE:
        return lang.snake_case(n)
    if e is Naming.CAMEL:
        return lang.camel_case(n)
    if e is Naming.LOW_CAMEL:
        r = lang.camel_case(n)
        return (r[0].lower() + r[1:]) if r else r
    raise ValueError(e)
